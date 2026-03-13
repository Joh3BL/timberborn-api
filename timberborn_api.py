import time
import requests
import urllib.parse


class TimberbornAPI:
    def __init__(self, base_url="http://localhost:8080/api", cache_ttl=8, on_any_change=None):
        """
        Initialize TimberbornAPI client.

        Args:
            base_url (str) (defaults to http://localhost:8080/api): Base URL for the Timberborn API.
            cache_ttl (float) (defaults to 8): Time-to-live for cached items in seconds.
            on_any_change (func): Called like a listener whenever any value has changed, before all other listeners.
                Called as (adaptor_name, current_state, prev_state). Can be used to log changes.
                If it is None, it won't call anything.
        """
        self.base_url = base_url.rstrip("/")
        self.cache_ttl = cache_ttl
        self.on_any_change = on_any_change

        self._lever_cache = {}
        self._adaptor_cache = {}
        self._listeners = {}

    # Helper to provide available methods
    @classmethod
    def methods(cls):
        import inspect
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
            name (str): The lever or adaptor name.

        Returns:
            str: URL-encoded name.
        """
        return urllib.parse.quote(name)

    @staticmethod
    def get_color(name: str):
        """
        Return a hex color code for a given color name.

        Args:
            name (str): Name of the color (e.g., "red", "green").

        Returns:
            str: Hex code string in format "#RRGGBB". Defaults to white.
        """
        colors = {
            "red": "#ff5050",
            "green": "#50ff78",
            "blue": "#5090ff",
            "yellow": "#ffdc50",
            "orange": "#ff9650",
            "purple": "#b478ff",
            "cyan": "#50ffff",
            "pink": "#ff78c8",
            "white": "#ffffff",
        }
        return colors.get(name.lower(), "#ffffff")

    # Internal cache helpers
    def _is_valid(self, obj):
        return time.monotonic() - obj["_ts"] < self.cache_ttl

    def _store(self, cache, obj):
        obj["_ts"] = time.monotonic()
        cache[obj["name"]] = obj
        return obj

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
        """
        name_enc = self.encode_name(name)
        lever = self._lever_cache.get(name)

        if lever and self._is_valid(lever):
            return lever

        r = requests.get(f"{self.base_url}/levers/{name_enc}")
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

    def set_lever(self, name, state: bool):
        """
        Set a lever's state if it differs from the current cached state.

        Args:
            name (str): Name of the lever (e.g., "lever 1").
            state (bool): Desired lever state.

        Returns:
            dict: Updated lever object.
        """
        lever = self.get_lever(name)
        if lever.get("state") == state:
            return lever

        name_enc = self.encode_name(name)
        r = requests.post(
            f"{self.base_url}/levers/{name_enc}",
            json={"state": state}
        )
        lever = r.json()
        return self._store(self._lever_cache, lever)

    def set_color(self, name, color_hex: str):
        """
        Set the color of a lever via the API.

        Args:
            name (str): Lever name (e.g., "lever 1").
            color_hex (str): Color hex string in format "#RRGGBB" or "RRGGBB".

        Returns:
            bool: True if HTTP request returned status 200, False otherwise.
        """
        if color_hex.startswith("#"):
            color_hex = color_hex[1:]
        name_enc = self.encode_name(name)
        r = requests.post(f"{self.base_url}/color/{name_enc}/{color_hex}")
        return r.status_code == 200

    # Adaptor methods
    def get_adaptor(self, name):
        """
        Get an adaptor by name, using cached data if available and recent.

        Args:
            name (str): Name of the adaptor (e.g., "adaptor 1").

        Returns:
            dict: Adaptor object, cached copy is used if TTL has not expired.
                Example:
                {
                    "name": "adaptor 1",
                    "state": True,
                    "_ts": 1710234512.483
                }
        """
        name_enc = self.encode_name(name)
        adaptor = self._adaptor_cache.get(name)

        if adaptor and self._is_valid(adaptor):
            return adaptor

        r = requests.get(f"{self.base_url}/adaptors/{name_enc}")
        adaptor = r.json()
        return self._store(self._adaptor_cache, adaptor)

    def list_adaptors(self):
        """
        Fetch the full list of adaptors from the API as a dict.

        This always makes an HTTP request and refreshes the internal cache.

        Returns:
            dict: Dictionary of adaptor objects, each like:
                {
                    # Template: [adaptor name]: 'state'
                    "adaptor 1": True,
                    "adaptor 2": False
                }
        """
        r = requests.get(f"{self.base_url}/adaptors")
        data = r.json()

        now = time.monotonic()
        result = {}

        for adaptor in data:
            adaptor["_ts"] = now
            self._adaptor_cache[adaptor["name"]] = adaptor
            result[adaptor["name"]] = adaptor["state"]

        return result

    # Listeners
    def register_listener(self, name, func):
        """
        Registers a function as a listener. 
        Function will be called as func(adaptor_name: str, current_state: bool, prev_state: bool)
        whenever the state of the adaptor it's registered to changes

        Args:
            name: (str): Name of the adaptor to listen to
            func: (function): Function to call whenever the state of the adaptor changes
                
        Example:
            api = TimberbornAPI()
            def my_listener(name, current_state, prev_state):
                print(f"State of {name} changed from {prev_state} to {current_state}.")
            
            api.register_listener("Adaptor 1")
            # Lever switched to on
            # Output: State of Adaptor 1 changed from False to True
        
        Notes:
            - Listeners are only triggered by changes detected in check_listeners(), which must be called
            - Listeners are called in the order they were registered for a given adaptor.
            - You can call register_listener multiple times for the same adaptor to register multiple functions, 
              and they will all be called when the state changes.
            - If the adaptor's state changes multiple times between calls to check_listeners(),
              the listener functions won't be called if the final state is the same as the initial state.
            - prev_state will be None for the first call to the listener, as prev_state is then unknown. 
        """

        if name not in self._listeners:
            self._listeners[name] = {'prev_state': None, 'funcs': [func]}
        else:
            self._listeners[name]['funcs'].append(func)

    def check_listeners(self):
        """
        Checks through all listener adaptors and checks if their value has changed.
        If it has changed, calls all functions in order registered.

        Notes:
            - Always updates cache, calls .list_adaptors() for new data. 
        """
        if not self._listeners:
            return

        data = self.list_adaptors()

        for adaptor_name, info_dict in self._listeners.items():
            prev_state = info_dict['prev_state']
            functions = info_dict['funcs']
            current_state = data.get(adaptor_name)

            if current_state is None:
                continue

            if prev_state == current_state:
                continue
            
            if self.on_any_change is not None:
                self.on_any_change(adaptor_name, current_state, prev_state)

            for func in functions:
                func(adaptor_name, current_state, prev_state)

            self._listeners[adaptor_name]['prev_state'] = current_state
    
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
            - This function may be difficult to exit and is intend as a shortcut for calling listeners.
            - If you want to exit the loop, provide an exit_condition(ticks_called_so_far) that
              at some point returns a True value.
            - You can also press Ctrl+C on your keyboard to exit the loop cleanly, this will return. 
        """

        tick = 0
        tick_seconds = ms_per_tick / 1000
        next_tick_time = time.monotonic()

        try:
            while not exit_condition(tick):
                start = time.monotonic()

                self.check_listeners()
                tick += 1

                next_tick_time += tick_seconds
                sleep_time = next_tick_time - time.monotonic()

                if sleep_time > 0:
                    time.sleep(sleep_time)
        except KeyboardInterrupt:
            return
    