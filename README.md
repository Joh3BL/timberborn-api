# Timberborn API

Python client for the [Timberborn](https://store.steampowered.com/app/1284200/Timberborn/) HTTP API.  
Provides easy control over levers, reading adaptors, and listening for state changes with caching for performance.

## Features

- Control levers: get and set their state.
- Read adaptors: fetch current adaptor states.
- Listener system: trigger callbacks on adaptor state changes.
- Fast caching with configurable TTL.
- Set lever colors using hex codes.

## Installation / Usage

### Install from github

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
api.set_color("Lever 1", "fffff") # Sets to white using hex

# List all levers
print(api.list_levers())

# Get adaptor state
adaptor = api.get_adaptor("Adaptor 1")
print(adaptor['state'])

# List all adaptors
print(api.list_adaptors())
```

### Listeners

```python
def my_listener(name, current_state, prev_state):
    print(f"{name} changed from {prev_state} to {current_state}")

api.register_listener("Adaptor 1", my_listener)

# Manually check for changes
api.check_listeners()

# Or activate automatic loop for (in this case) 10 ticks.
api.activate_listener_loop(
    ms_per_tick=2000, 
    exit_condition=lambda ticks: ticks > 10
    )
```

### Logic Gates

Logic gates can be used to simulate the relay logic from [Timberborn](https://store.steampowered.com/app/1284200/Timberborn/). This allows for easy, simple to update complex logic. More thorough examples can be found in the [examples]("https://github.com/Joh3BL/timberborn-api/tree/main/examples") folder.

```python
# Import Lever and Adaptor wrappers for logic gates
from timberborn_api import TimberbornAPI, L, A

api = TimberbornAPI()

# Turns off lever 1 when adaptor 1 is off
def turn_of_lever_1(name, current_state, prev_state):
    api.set_lever(
        "lever 1", 
        api.and_("adaptor 1", L("lever 1"))
        )

api.register_listener("adaptor 1", turn_of_lever_1)

# Manually check if adaptor 1 is off
api.check_listeners()

# Check NOR for adaptor 2 and lever 2
print(api.or_(*api.not_( # Reverts all inputs, simulates NOR gate
    A("adaptor 2"), L("lever 2")
    )))
```

As not\_ returns a list whenever you have multiple arguments, you can use a not\_ gate to simulate reverse gates, like NAND and NOR. Remember to use **\***api.not\_ so that the list gets unpacked into *\*args*.

## API Reference

All methods are available with the `TimberbornAPI` class.
Use `TimberbornAPI.methods()` to list all public methods, or use __docstrings__ (.\_\_doc\_\_) on a method to access a description in detail on what it does.

### Methods

- get_lever(name: str)
- set_lever(name: str, state: bool)
- set_color(name: str, color_hex)
- list_levers()
- get_adaptor(name: str)
- list_adaptors()
- register_listener(name: str, func: callable)
- check_listeners()
- activate_listener_loop(exit_condition=lambda ticks: False, ms_per_tick=5000)
- not_(*args)
- and_(*args)
- or_(*args)
- xor_(*args)

### Examples

If you have any other questions to how this works or how it can be used,  
please refer to the [examples]("https://github.com/Joh3BL/timberborn-api/tree/main/examples").

## Configuration

- *base_url* (str): URL of your Timberborn API server (default: `http//localhost:8080/api`)
- *cache_ttl* (float): Cache *Time To Live* in seconds (default: 8). Used for get_lever/get_adaptor
- *on_any_change* (callable): Optional global callback when any adaptor changes

## Contibuting

Contributions are welcome!
Please open an issue or submit a pull request on [Github](https://github.com/Joh3BL/timberborn-api/pulls).

## License

This project is licensed under the MIT License. See the [LICENCE](https://github.com/Joh3BL/timberborn-api/blob/main/LICENSE) file for more information
