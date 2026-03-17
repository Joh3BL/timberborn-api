"""
Timberborn API client for Python.
Read README.md for usage instructions.
Examples can be found in the examples/ folder.
Authors:
  - Joh3BL

"""

from threading import Thread, Lock
from typing import Union
import urllib.parse
import inspect
import time
import logging  # Used to silence Flask logs in _start_adapter_server

from flask import Flask
import requests


ConditionItem = Union[bool, str, "TimberbornAPI.Lever", "TimberbornAPI.Adapter"]

# pylint: disable=too-many-instance-attributes
class TimberbornAPI:
    """Timberborn API client with caching, listeners, and logic modules."""

    def __init__(
            self,
            base_url="http://localhost:8080/api",
            adapter_listener_port=8081,
            cache_ttl=8,
            on_any_change=None):
        """
        Initialize TimberbornAPI client.

        Args:
            base_url (str) (defaults to http://localhost:8080/api): 
                Base URL for the Timberborn API.
            cache_ttl (float) (defaults to 8): 
                Time-to-live for cached items in seconds.
            adapter_listener_port (int) (defaults to 8081): 
                Port to listen for adapter change events. 
                This should match the port configured in Timberborn for sending adapter updates.
            on_any_change (func): 
                Called like a listener whenever any value has changed, before all other listeners.
                Called as (adapter_name, current_state, prev_state). Can be used to log changes.
                If it is None, it won't call anything.
        """
        self.base_url = base_url.rstrip("/")
        self.adapter_port = adapter_listener_port
        self.cache_ttl = cache_ttl
        self.on_any_change = on_any_change

        self._lock = Lock()

        self._lever_cache = {}
        self._adapter_cache = {}
        self._lever_listeners = {}
        self._adapter_listeners = {}

        self._start_adapter_server() # Start the background Flask server for adapters

    # Wrapper classes for levers and adapters
    class Lever:
        """
        Object that indicates a name is a lever, or can be used in OOP
        to switch on and off levers and set their color.
        Result when get_lever or list_levers is called or when L() is used.
        """
        def __init__(self, api, name):
            self._api = api
            self.name = name

        @property
        def state(self):
            """Current state of the lever (True = on, False = off)."""
            return self._api._get_lever_dict(self.name)['state']

        @state.setter
        def state(self, value):
            """Set the lever state via the API when assigned to."""
            self._api.set_lever(self.name, value)
        
        @property
        def spring_return(self):
            return self._api._get_lever_dict(self.name)['springReturn']

        def switch_on(self):
            """Switch the lever on via the API."""
            self._api.set_lever(self.name, True)

        def switch_off(self):
            """Switch the lever off via the API."""
            self._api.set_lever(self.name, False)   

        def toggle(self):
            """Toggle the lever state via the API."""
            self.state = not self.state

        def set_color(self, color_hex: str):
            """Set the lever color via the API."""
            self._api.set_color(self.name, color_hex)

        def __str__(self):
            return self.name

        def __repr__(self):
            return f"L({self.name})"

    class Adapter:
        """
        Object that indicate a name is an adapter.
        Result when get_adapter or list_adapters is called or when A() is used.
        """
        def __init__(self, api, name):
            self._api = api
            self.name = name
        
        @property
        def state(self):
            return self._api._get_adapter_dict(self.name)['state']

        def __str__(self):
            return self.name

        def __repr__(self):
            return f"A({self.name})"

    # Convenience wrappers for users
    def L(self, name):  # pylint: disable=C0103
        """Convenience wrapper to indicate a lever name."""
        return self.get_lever(name)

    def A(self, name):  # pylint: disable=C0103
        """Convenience wrapper to indicate an adapter name."""
        return self.get_adapter(name)

    # Helper to provide available methods
    @classmethod
    def methods(cls):
        """Returns a list of available method names for the TimberbornAPI class."""
        return [
            name for name, func in inspect.getmembers(cls, inspect.isfunction)
            if not name.startswith("_")
        ]

    # Utility helpers
    @staticmethod
    def _encode_name(name: str) -> str:
        """
        URL-encode a name for HTTP requests.

        Args:
            name (str): The lever or adapter name.

        Returns:
            str: URL-encoded name.
        """
        return urllib.parse.quote(name)

    # Internal cache helpers
    def _is_valid(self, obj):
        return time.monotonic() - obj["_ts"] < self.cache_ttl

    def _store(self, cache, obj):
        obj = obj.copy()
        obj["_ts"] = time.monotonic()
        with self._lock:
            cache[obj["name"]] = obj
        return obj

    @staticmethod
    def _check_response(r):
        if r.status_code == 404:
            raise RuntimeError(r.text)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text}")

    # Lever methods
    def _get_lever_dict(self, name):
        """
        Internal helper to get cached or fresh response from the api.

        Returns:
            dict: Dictionary of properties, like for example:
                {
                    'name': 'lever 1',
                    'state': True,
                    'springReturn': False
                }
        """

        name_enc = self._encode_name(name)
        lever = self._lever_cache.get(name)

        if lever and self._is_valid(lever):
            return lever.copy()

        r = requests.get(f"{self.base_url}/levers/{name_enc}", timeout=5)

        self._check_response(r)

        lever = r.json()
        return self._store(self._lever_cache, lever)

    def get_lever(self, name):
        """
        Get a lever by name, using cached data if available and recent.

        Args:
            name (str): Name of the lever (e.g., "lever 1").

        Returns:
            Lever: A Lever object with attributes like name, state, and spring_return.
            Cached copy is used if TTL has not expired.
        
        Raises:
            RuntimeError: If the lever does not exist on the server or the request fails.
        """

        lever_dict = self._get_lever_dict(name)

        return self.Lever(
            api=self,
            name=lever_dict["name"]
        )

    def list_levers(self):
        """
        Fetch the full list of levers from the API as a dict.

        This always makes an HTTP request and refreshes the internal cache.

        Returns:
            dict: Dictionary of Lever objects, each like:
                {
                    "lever 1": Lever(name="lever 1", state=True, spring_return=False),
                    "lever 2": Lever(name="lever 2", state=False, spring_return=True)
                }
        """
        r = requests.get(f"{self.base_url}/levers", timeout=5)
        data = r.json()

        now = time.monotonic()
        result = {}

        for lever in data:
            lever_copy = lever.copy()
            lever_copy["_ts"] = now

            with self._lock:
                self._lever_cache[lever["name"]] = lever_copy

            result[lever["name"]] = self.Lever(
                api=self,
                name=lever["name"]
            )

        return result

    def set_lever(self, name: str, state: bool):
        """
        Set a lever's state via the Timberborn API.

        Args:
            name (str): Name of the lever (e.g., "lever 1").
            state (bool): Desired lever state (True = on, False = off).

        Returns:
            Lever: Updated lever object.

        Raises:
            RuntimeError: If the lever does not exist or the request fails.
        """
        lever = self._get_lever_dict(name)
        if lever.get("state") == state and not lever.get('springReturn'):
            return self.Lever(api=self, name=name)

        name_enc = self._encode_name(name)
        endpoint = "switch-on" if state else "switch-off"

        r = requests.post(f"{self.base_url}/{endpoint}/{name_enc}", timeout=5)

        self._check_response(r)

        lever["state"] = state
        returned = self._store(self._lever_cache, lever)
        return self.Lever(
            api=self,
            name=name
        )

    def set_color(self, name, color_hex: str):
        """
        Set the color of a lever via the API.

        Args:
            name (str): Lever name (e.g., "lever 1").
            color_hex (str): Color hex string in format "#RRGGBB" or "RRGGBB".

        Returns:
            bool: True if the color was successfully set, i.e. the code executed.
        
        Raises:
            RuntimeError: If the lever does not exist or the request fails.
        """
        if color_hex.startswith("#"):
            color_hex = color_hex[1:]

        name_enc = self._encode_name(name)
        r = requests.post(f"{self.base_url}/color/{name_enc}/{color_hex}", timeout=5)

        self._check_response(r)

        return True

    # Adapter methods
    def _get_adapter_dict(self, name):
        """
        Internal helper to get cached or fresh response from the api.

        Returns:
            dict: Dictionary of properties, like for example:
                {
                    'name': 'adapter 1',
                    'state': True,
                }
        """

        name_enc = self._encode_name(name)
        adapter = self._adapter_cache.get(name)

        if adapter and self._is_valid(adapter):
            return adapter.copy()

        r = requests.get(f"{self.base_url}/adapters/{name_enc}", timeout=5)

        self._check_response(r)

        adapter = r.json()
        return self._store(self._adapter_cache, adapter)

    def get_adapter(self, name):
        """
        Get an adapter by name, using cached data if available and recent.

        Args:
            name (str): Name of the adapter (e.g., "adapter 1").

        Returns:
            Adapter: A Adapter object with attributes like name and state.
            Cached copy is used if TTL has not expired.

        Raises:
            RuntimeError: If the adapter does not exist on the server or the request fails.
        """

        adapter_dict = self._get_adapter_dict(name)

        return self.Adapter(
            api=self,
            name=adapter_dict["name"]
        )

    def list_adapters(self):
        """
        Fetch the full list of adapters from the API as a dict.

        This always makes an HTTP request and refreshes the internal cache.

        Returns:
            dict: Dictionary of adapter objects, each like:
                {
                    "adapter 1": Adapter(name="adapter 1", state=True),
                    "adapter 2": Adapter(name="adapter 2", state=False)
                }
        """
        r = requests.get(f"{self.base_url}/adapters", timeout=5)
        data = r.json()

        now = time.monotonic()
        result = {}

        for adapter in data:
            adapter_copy = adapter.copy()
            adapter_copy["_ts"] = now
            self._adapter_cache[adapter["name"]] = adapter_copy
            result[adapter["name"]] = self.Adapter(
                api=self,
                name=adapter["name"]
            )

        return result

    # Listeners
    def register_lever_listener(self, name, func):
        """
        Registers a function as a listener. 
        Function will be called as func(lever_name: str, current_state: bool, prev_state: bool)
        whenever the state of the lever it's registered to changes

        Args:
            name: (str): Name of the lever to listen to
            func: (function): Function to call whenever the state of the lever changes
                
        Example:
            api = TimberbornAPI()
            def my_listener(name, current_state, prev_state):
                print(f"State of {name} changed from {prev_state} to {current_state}.")
            
            api.register_listener("Lever 1")
            # Lever switched to on
            # Output: State of Lever 1 changed from False to True
        
        Notes:
            - Lever listeners are only triggered by changes detected in check_listeners(), 
              which must be called, or use activate_lever_listener_loop().
            - Listeners are called in the order they were registered for a given lever.
            - You can call register_lever_listener multiple times for the same lever to register 
              multiple functions, and they will all be called when the state changes.
            - If the lever's state changes multiple times between calls to check_listeners(),
              the listener functions won't be called if the final state 
              is the same as the initial state.
            - prev_state will be None for the first call to the listener, 
              as prev_state is then unknown. 
        """

        with self._lock:
            if name not in self._lever_listeners:
                self._lever_listeners[name] = {'prev_state': None, 'funcs': [func]}
            else:
                self._lever_listeners[name]['funcs'].append(func)

    def register_adapter_listener(self, name, func):
        """
        Registers a function as an adapter listener.
        Called like func(adapter_name, current_state, prev_state).

        See register_lever_listener.__doc__ for more details,
        it works the same but for adapters instead of levers.

        This one however works with Timberborns API adapter updates,
        so it might be more responsive, reliable and efficient than lever listeners.
        """
        with self._lock:
            if name not in self._adapter_listeners:
                self._adapter_listeners[name] = {'funcs': [func], 'prev_state': None}
            else:
                self._adapter_listeners[name]['funcs'].append(func)

    def check_lever_listeners(self):
        """
        Checks through all listener levers and checks if their value has changed.
        If it has changed, calls all functions in order registered.

        Notes:
            - Always updates cache, calls .list_levers() for new data. 
        """
        if not self._lever_listeners:
            return

        data = self.list_levers()

        for lever_name, info_dict in self._lever_listeners.items():
            lever = data.get(lever_name)

            current_state = lever.state if lever else None

            if current_state is None:
                continue

            if info_dict['prev_state'] == current_state:
                continue

            if self.on_any_change is not None:
                self.on_any_change(lever_name, current_state, info_dict['prev_state'])

            for func in info_dict['funcs']:
                func(lever_name, current_state, info_dict['prev_state'])

            info_dict['prev_state'] = current_state

    def activate_lever_listener_loop(self, exit_condition=lambda ticks: False, ms_per_tick=5000):
        """ 
        Initiates a while (not exit_condition(tick_count)) loop, that calls .check_listeners().
        Exits when exit_condition returns True.

        Args:
            exit_condition (func) (defaults to lambda ticks: False):
                Is called in the while loop, when it returns True, it is exited.
            ms_per_tick (float): 
                Amount of milliseconds per tick the loop will aim for.
                If it is too small, some ticks may be missed, due to missing the time point
                when the function would've been called.
        
        Notes:
            - This function may be difficult to exit and it's intend as a shortcut
              for users who want to use listeners without having to call check_listeners().
            - If you want to exit the loop, provide an exit_condition(ticks_called_so_far) that
              at some point returns a True value, or you can raise KeyboardInterrupt.
            - You can also press Ctrl+C on your keyboard to exit the loop cleanly, this will return. 
        """

        tick = 0
        tick_seconds = ms_per_tick / 1000
        next_tick_time = time.monotonic()

        try:
            while not exit_condition(tick):
                self.check_lever_listeners()
                tick += 1

                next_tick_time += tick_seconds
                sleep_time = next_tick_time - time.monotonic()

                if sleep_time > 0:
                    time.sleep(sleep_time)
        except KeyboardInterrupt:
            pass

    def initialize_adapter_prev_states(self):
        """
        Initialize all adapter listeners with their current state.

        For each adapter listener:
          - Calls all registered functions with:
             (adapter_name = name of the adapter
              current_state = current API state
              prev_state = previously recorded state, or None if not yet set)
          - Updates the internal prev_state to the current state

        Notes:
            - This is useful to sync listener states when starting the game or refreshing.
            - Not required, but can be useful.
        """
        # Fetch latest adapter states from the API
        current_adapters = self.list_adapters()

        for adapter_name, info_dict in self._adapter_listeners.items():
            prev_state = info_dict.get('prev_state', None)
            adapt_obj = current_adapters.get(adapter_name)
            current_state = adapt_obj.state if adapt_obj else None

            if current_state is None:
                # Adapter not found, skip
                continue

            # Call all registered functions
            for func in info_dict['funcs']:
                func(adapter_name, current_state, prev_state)

            # Update prev_state to current API state
            info_dict['prev_state'] = current_state

    def _trigger_adapter(self, adapter_name, current_state):
        """Call registered callbacks when an adapter changes state."""
        with self._lock:
            if adapter_name not in self._adapter_listeners:
                return

            prev_state = self._adapter_listeners[adapter_name]['prev_state']
            if prev_state == current_state:
                return

            funcs = list(self._adapter_listeners[adapter_name]['funcs'])
            self._adapter_listeners[adapter_name]['prev_state'] = current_state
        

        # Optional global hook
        if self.on_any_change is not None:
            self.on_any_change(adapter_name, current_state, prev_state)

        # Call all registered functions
        for func in funcs:
            func(adapter_name, current_state, prev_state)

    def _start_adapter_server(self):
        """Starts a Flask server to listen for adapter GET requests."""
        app = Flask(__name__)

        # Silence the Flask/Werkzeug info messages
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        app.logger.setLevel(logging.ERROR)

        @app.route("/on/<adapter_name>", methods=["GET", "POST"])
        def on_adapter(adapter_name):
            adapter_name = urllib.parse.unquote(adapter_name)
            self._trigger_adapter(adapter_name, True)
            return "OK", 200

        @app.route("/off/<adapter_name>", methods=["GET", "POST"])
        def off_adapter(adapter_name):
            adapter_name = urllib.parse.unquote(adapter_name)
            self._trigger_adapter(adapter_name, False)
            return "OK", 200

        def run():
            app.run(port=self.adapter_port, debug=False, use_reloader=False, threaded=True)

        thread = Thread(target=run, daemon=True)
        thread.start()

    # Logic modules
    def _turn_to_bool(self, arg: ConditionItem) -> bool:
        """
        Returns ready booleans as themselves.  
        By default, interprets strings as adapter names,  
        or gets the state of a wrapped Lever or Adapter name.
        """
        if isinstance(arg, bool):
            return arg
        if isinstance(arg, str):
            return self.get_adapter(arg).state
        if isinstance(arg, TimberbornAPI.Lever):
            return arg.state
        if isinstance(arg, TimberbornAPI.Adapter):
            return arg.state
        raise TypeError(f"Unsupported condition item type: {type(arg)}")

    def not_(self, *args):
        """
        Negates all inputs. 
        
        Args:
            Some ConditionItem(s):
                Bool, 
                string that is an adapter name
                A() wrapper (adapter)
                L() wrapper (lever)

        Returns:
          - single boolean if only one input
          - list of booleans if multiple inputs
        """
        results = [not self._turn_to_bool(arg) for arg in args]
        if len(results) == 1:
            return results[0]  # single boolean for convenience
        return results      # list if multiple

    def and_(self, *args) -> bool:
        """
        Returns: True if all inputs evaluate to True

        Args:
            Some ConditionItem(s):
                Bool, 
                string that is an adapter name
                A() wrapper (adapter)
                L() wrapper (lever)
        """
        return all(self._turn_to_bool(arg) for arg in args)

    def or_(self, *args) -> bool:
        """
        Returns: True if any input evaluates to True

        Args:
            Some ConditionItem(s):
                Bool, 
                string that is an adapter name
                A() wrapper (adapter)
                L() wrapper (lever)
        """
        return any(self._turn_to_bool(arg) for arg in args)

    def xor_(self, *args) -> bool:
        """
        Returns: True if an odd number of inputs evaluate to True.
        For two inputs: Return True if exactly one input is True.

        Args:
            Some ConditionItem(s):
                Bool, 
                string that is an adapter name
                A() wrapper (adapter)
                L() wrapper (lever)
        """
        return sum(self._turn_to_bool(arg) for arg in args) % 2 == 1
