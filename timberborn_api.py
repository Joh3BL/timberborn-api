"""
Timberborn API client for Python.
Read README.md for usage instructions.
Examples can be found in the examples/ folder.
Authors:
  - Joh3BL

"""

from typing import Union
import urllib.parse
import inspect
import time
import requests

class TimberbornAPI:
    """
    Main API client class for interacting with the Timberborn API.
    Provides methods to get and set levers, get adapters, and register listeners.
    Call TimberbornAPI.methods() to get a list of available methods.
    """
    def __init__(self, base_url="http://localhost:8080/api", cache_ttl=8, on_any_change=None):
        """
        Initialize TimberbornAPI client.

        Args:
            base_url (str) (defaults to http://localhost:8080/api): Base URL for the Timberborn API.
            cache_ttl (float) (defaults to 8): Time-to-live for cached items in seconds.
            on_any_change (func): 
                Called like a listener whenever any value has changed, before all other listeners.
                Called as (adapter_name, current_state, prev_state). Can be used to log changes.
                If it is None, it won't call anything.
        """
        self.base_url = base_url.rstrip("/")
        self.cache_ttl = cache_ttl
        self.on_any_change = on_any_change

        self._lever_cache = {}
        self._adapter_cache = {}
        self._listeners = {}

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
    def encode_name(name: str) -> str:
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
        obj["_ts"] = time.monotonic()
        cache[obj["name"]] = obj
        return obj

    @staticmethod
    def _check_response(r):
        if r.status_code == 404:
            raise RuntimeError(r.text)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text}")

    # Lever methods
    def get_lever(self, name):
        """
        Get a lever by name, using cached data if available and recent.

        Args:
            name (str): Name of the lever (e.g., "lever 1").

        Returns:
            dict: Lever object containing at least:
                {
                    "name": "lever 1",
                    "state": True,
                    "springReturn": False,
                    "_ts": 1710234512.483
                }
            Cached copy is used if TTL has not expired.
        
        Raises:
            RuntimeError: If the lever does not exist on the server or the request fails.
        """
        name_enc = self.encode_name(name)
        lever = self._lever_cache.get(name)

        if lever and self._is_valid(lever):
            return lever

        r = requests.get(f"{self.base_url}/levers/{name_enc}")

        self._check_response(r)

        lever = r.json()
        return self._store(self._lever_cache, lever)

    def list_levers(self):
        """
        Fetch the full list of levers from the API as a dict.

        This always makes an HTTP request and refreshes the internal cache.

        Returns:
            dict: Dictionary of lever objects, each like:
                {
                    "lever 1": {
                        "state": True, 
                        "springReturn": False
                    },
                    "lever 2": {
                        "state": False,
                        "springReturn": False
                    }
                }
        """
        r = requests.get(f"{self.base_url}/levers")
        data = r.json()

        now = time.monotonic()
        result = {}

        for lever in data:
            lever["_ts"] = now
            self._lever_cache[lever["name"]] = lever
            result[lever["name"]] = {
                "state": lever["state"],
                "springReturn": lever["springReturn"]
            }

        return result

    def set_lever(self, name: str, state: bool):
        """
        Set a lever's state via the Timberborn API.

        Args:
            name (str): Name of the lever (e.g., "lever 1").
            state (bool): Desired lever state (True = on, False = off).

        Returns:
            dict: Updated lever object.

        Raises:
            RuntimeError: If the lever does not exist or the request fails.
        """
        lever = self.get_lever(name)
        if lever.get("state") == state:
            return lever

        name_enc = self.encode_name(name)
        endpoint = "switch-on" if state else "switch-off"

        r = requests.post(f"{self.base_url}/{endpoint}/{name_enc}")

        self._check_response(r)

        lever["state"] = state
        return self._store(self._lever_cache, lever)

    def set_color(self, name, color_hex: str):
        """
        Set the color of a lever via the API.

        Args:
            name (str): Lever name (e.g., "lever 1").
            color_hex (str): Color hex string in format "#RRGGBB" or "RRGGBB".

        Returns:
            bool: True if HTTP request returned status 200, False otherwise.
        
        Raises:
            RuntimeError: If the lever does not exist or the request fails.
        """

        if color_hex.startswith("#"):
            color_hex = color_hex[1:]

        name_enc = self.encode_name(name)
        r = requests.post(f"{self.base_url}/color/{name_enc}/{color_hex}")

        self._check_response(r)

        return True

    # Adapter methods
    def get_adapter(self, name):
        """
        Get an adapter by name, using cached data if available and recent.

        Args:
            name (str): Name of the adapter (e.g., "adapter 1").

        Returns:
            dict: Adapter object, cached copy is used if TTL has not expired.
                Example:
                {
                    "name": "adapter 1",
                    "state": True,
                    "_ts": 1710234512.483
                }
        
        Raises:
            RuntimeError: If the adapter does not exist on the server or the request fails.
        """
        name_enc = self.encode_name(name)
        adapter = self._adapter_cache.get(name)

        if adapter and self._is_valid(adapter):
            return adapter

        r = requests.get(f"{self.base_url}/adapters/{name_enc}")

        self._check_response(r)

        adapter = r.json()
        return self._store(self._adapter_cache, adapter)

    def list_adapters(self):
        """
        Fetch the full list of adapters from the API as a dict.

        This always makes an HTTP request and refreshes the internal cache.

        Returns:
            dict: Dictionary of adapter objects, each like:
                {
                    # Template: [adapter name]: 'state'
                    "adapter 1": True,
                    "adapter 2": False
                }
        """
        r = requests.get(f"{self.base_url}/adapters")
        data = r.json()

        now = time.monotonic()
        result = {}

        for adapter in data:
            adapter["_ts"] = now
            self._adapter_cache[adapter["name"]] = adapter
            result[adapter["name"]] = adapter["state"]

        return result

    # Listeners
    def register_listener(self, name, func):
        """
        Registers a function as a listener. 
        Function will be called as func(adapter_name: str, current_state: bool, prev_state: bool)
        whenever the state of the adapter it's registered to changes

        Args:
            name: (str): Name of the adapter to listen to
            func: (function): Function to call whenever the state of the adapter changes
                
        Example:
            api = TimberbornAPI()
            def my_listener(name, current_state, prev_state):
                print(f"State of {name} changed from {prev_state} to {current_state}.")
            
            api.register_listener("Adapter 1")
            # Lever switched to on
            # Output: State of Adapter 1 changed from False to True
        
        Notes:
            - Listeners are only triggered by changes detected in check_listeners(), 
              so you need to call the function, or activate_lever_listener_loop().
            - Listeners are called in the order they were registered for a given adapter.
            - You can call register_listener multiple times for the same adapter to 
              register multiple functions, and they will all be called when the state changes.
            - If the adapter's state changes multiple times between calls to check_listeners(),
              the listener functions won't be called if the final state didn't change.
            - prev_state will be None for the first call to the listener, 
              as prev_state is then unknown. This always triggers the listener.
        """

        if name not in self._listeners:
            self._listeners[name] = {'prev_state': None, 'funcs': [func]}
        else:
            self._listeners[name]['funcs'].append(func)

    def check_listeners(self):
        """
        Checks through all listener adapters and checks if their value has changed.
        If it has changed, calls all functions in order registered.

        Notes:
            - Always updates cache, calls .list_adapters() for new data.
        """
        if not self._listeners:
            return

        data = self.list_adapters()

        for adapter_name, info_dict in self._listeners.items():
            current_state = data.get(adapter_name)

            if current_state is None:
                continue

            if info_dict['prev_state'] == current_state:
                continue

            if self.on_any_change is not None:
                self.on_any_change(adapter_name, current_state, info_dict['prev_state'])

            for func in info_dict['funcs']:
                func(adapter_name, current_state, info_dict['prev_state'])

            self._listeners[adapter_name]['prev_state'] = current_state

    def activate_listener_loop(self, exit_condition=lambda ticks: False, ms_per_tick=5000):
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
              at some point returns a True value.
            - You can also press Ctrl+C on your keyboard to exit the loop cleanly, this will return. 
        """

        tick = 0
        tick_seconds = ms_per_tick / 1000
        next_tick_time = time.monotonic()

        try:
            while not exit_condition(tick):
                self.check_listeners()
                tick += 1

                next_tick_time += tick_seconds
                sleep_time = next_tick_time - time.monotonic()

                if sleep_time > 0:
                    time.sleep(sleep_time)
        except KeyboardInterrupt:
            pass

    # Logic modules
    ConditionItem = Union[bool, str, 'Lever', 'Adapter']

    def _turn_to_bool(self, arg: ConditionItem) -> bool:
        """
        Returns ready booleans as themselves.  
        By default, interprets strings as adapter names,  
        or gets the state of a wrapped Lever or Adapter name.
        """
        if isinstance(arg, bool):
            return arg
        if isinstance(arg, str):
            return self.get_adapter(arg)['state']
        if isinstance(arg, Lever):
            return self.get_lever(arg.name)['state']
        if isinstance(arg, Adapter):
            return self.get_adapter(arg.name)['state']
        raise TypeError(f"Unknown condition type {arg}")

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
        results = [self._turn_to_bool(arg) for arg in args]
        return all(results)

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
        results = [self._turn_to_bool(arg) for arg in args]
        return any(results)

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
        results = [self._turn_to_bool(arg) for arg in args]
        return sum(results) % 2 == 1


class Lever:
    """
    Wrapper to inicate string is a lever name.
    Currently only used for logic. 
    """
    def __init__(self, name):
        self.name = name

class Adapter:
    """
    Wrapper to indicate string is an adapter name.
    Currently only used for logic. 
    """
    def __init__(self, name):
        self.name = name

# Short aliases for convenience
L = Lever
A = Adapter
