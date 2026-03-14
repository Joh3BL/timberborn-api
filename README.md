# Timberborn API

Python client for the [Timberborn](https://store.steampowered.com/app/1284200/Timberborn/) HTTP API.  
Provides easy control over levers, reading adapters, and listening for state changes with caching for performance.

## Features

- Control levers: get and set their state.
- Read adapters: fetch current adapter states.
- Listener system: trigger callbacks on adapter state changes.
- Fast caching with configurable TTL.
- Set lever colors using hex codes.

## Installation / Usage

### Install from github via pip

This *\*should\** install dependencies

```bash
pip install git+https://github.com/Joh3BL/timberborn-api.git
```

### Or clone the repository

```bash
git clone https://github.com/Joh3BL/timberborn-api.git
cd timberborn-api
```

### Then import it into your project

```python
from timberborn_api import TimberbornAPI
```

## Usage

### Preparations

1. When launching the game, you need to click on an HTTP Lever or Adapter,
   and turn on the API. This will establish the connection
2. Make sure that the port for levers is 8080 (`http://localhost:8080`),
   if it's not, initialize api with base_url as the proper address.
3. If you are using adapter listeners, turn on the two checkboxes for posting
   when the adapter turns on and off. This will then use the Flask server, and call your code.
     You also need to verify that the port for the adapter's is 8081, if it's not,
   initialize api with adapter_listener_port as the proper code.
4. If you plan on contributing, you can use a main.py file, as the git won't upload your test code.

### Basic Example

```python
from timberborn_api import TimberbornAPI

api = TimberbornAPI()

# Set lever state
api.set_lever("Lever 1", True)

# Get lever state
lever = api.get_lever("Lever 1")
print(lever['state']) 
# True as long as lever exists in timberborn

# Set a lever color
api.set_color("Lever 1", "ffffff") # Sets to white using hex

# List all levers
print(api.list_levers())

# Get adapter state
adapter = api.get_adapter("Adapter 1")
print(adapter['state'])

# List all adapters
print(api.list_adapters())
```

### Listeners

```python
# Register a lever listener
def my_listener(lever_name, current_state, prev_state):
    print(f"{lever_name} changed from {prev_state} to {current_state}")

api.register_lever_listener("Lever 1", my_listener)

# Manually check for changes
api.check_listeners()

# Or activate automatic loop for (in this case) 10 ticks. (Only for lever listeners)
api.activate_lever_listener_loop(
    ms_per_tick=2000, 
    exit_condition=lambda ticks: ticks > 10
    )

# Register an adapter listener running on Flask server:
def adapter_listener(adapter_name, current_state, prev_state):
    print(f"{adapter_name} changed from {prev_state} to {current_state}")

api.register_adapter_listener("Adapter 1", adapter_listener)
# The adapter listener runs whenever Timberborn sends adapter changes,
# turn on the checkboxes in the adapter window
```

### Logic Gates

Logic gates can be used to simulate the relay logic from [Timberborn](https://store.steampowered.com/app/1284200/Timberborn/). This allows for easy, simple to update complex logic. More thorough examples can be found in the [Examples](https://github.com/Joh3BL/timberborn-api/tree/main/examples) folder.

```python
# Import Lever and Adapter wrappers for logic gates
from timberborn_api import TimberbornAPI, L, A

api = TimberbornAPI()

# Turns off lever 1 when adapter 1 is off
def turn_off_lever_1(name, current_state, prev_state):
    api.set_lever(
        "Lever 1", 
        api.and_("Adapter 1", L("Lever 1"))
        )

api.register_adapter_listener("adapter 1", turn_off_lever_1)

#TODO: Add manual check of adapter listener to initialize!

# Check NOR for adapter 2 and lever 2
print(api.or_(*api.not_( # Reverts all inputs, simulates NOR gate
    A("adapter 2"), L("lever 2")
    )))
```

As not\_ returns a list whenever you have multiple arguments, you can use a not\_ gate to simulate reverse gates, like NAND and NOR. Remember to use **\***api.not\_ so that the list gets unpacked into *\*args*. not\_ returns just a boolean when only 1 value is given.

## API Reference

All methods are available with the `TimberbornAPI` class.
Use `TimberbornAPI.methods()` to list all public methods, or use **docstrings** *(.\_\_doc\_\_)* on a method to access a description in detail on what it does.

### Methods

- `get_lever(name: str)`
- `set_lever(name: str, state: bool)`
- `set_color(name: str, color_hex)`
- `list_levers()`
- `get_adapter(name: str)`
- `list_adapters()`
- `register_lever_listener(name: str, func: callable)`
- `register_adapter_listener(name: str, func: callable)`
- `check_lever_listeners()`
- `activate_lever_listener_loop(exit_condition=lambda ticks: False, ms_per_tick=5000)`
- `not_(*args)`
- `and_(*args)`
- `or_(*args)`
- `xor_(*args)`

For the logic gates, you need to import the wrappers, L(), A()

### Examples

If you have any other questions to how this works or how it can be used,  
please refer to the [examples](https://github.com/Joh3BL/timberborn-api/tree/main/examples).

## Configuration

api = `TimberbornAPI()` arguments:

- *base_url* (str): URL of your Timberborn API server (default: `http://localhost:8080/api`)
- *adapter_listener_port* (str): Port for adapter calls (default: `8081`)
- *cache_ttl* (float): Cache *Time To Live* in seconds (default: 8). Used for get_lever/get_adapter
- *on_any_change* (callable): Optional global callback when any adapter changes

## Contibuting

Contributions are welcome!

If you find a bug or have a feature request,
please open an [Issue](https://github.com/Joh3BL/timberborn-api/issues).

If you'd like to contribute code:

1. Fork the repository
2. Create a branch
3. Submit a [Pull Request](https://github.com/Joh3BL/timberborn-api/pulls)

## License

This project is licensed under the MIT License. See the [LICENCE](https://github.com/Joh3BL/timberborn-api/blob/main/LICENSE) file for more information
