# Timberborn API

Python client for the [Timberborn](https://store.steampowered.com/app/1284200/Timberborn/) HTTP API.  
Provides easy control over levers, reading adapters, and listening for state changes with caching for performance.

## Features

- *Control levers*: get and set their state.
- *Set lever colors*: using hex codes.
- *Read adapters*: fetch current adapter states.
- *Listener system*: trigger callbacks on adapter or lever state changes.
- *Fast caching*: with configurable TTL.
- *Use Timberborn's own* **adapter change system** for *listeners*.

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

1. When launching the game, you need to click on an `HTTP Lever` or `HTTP Adapter`,
   and turn on the API. This will establish the connection
2. Make sure that the the base api port is **8080** (`http://localhost:8080`),
   if it's not, initialize *api* with `base_url` as the proper address.
     You can easily check this by clicking on a lever and checking if the url says:
   `http://localhost:8080/api/switch-on/{lever_name}`.
3. If you are using `adapter listeners`, turn on the two checkboxes for posting
   when the adapter turns on and off. This will then use the *Flask server*, and call your code.
     You also need to verify that the port that the adapter's use is `8081`, if it's not,
   initialize *api* with `adapter_listener_port` set to the correct port number. You can check this by looking at the url below the checkboxes, and checking if it is: `http://localhost:8081/api/on/{adapter_name}`.
4. If you plan on contributing, use a `main.py` file to avoid committing test scripts to Git.

### Basic Example

```python
from timberborn_api import TimberbornAPI

api = TimberbornAPI()

# Set lever state
api.set_lever("Lever 1", True)

# Get lever state
lever = api.get_lever("Lever 1")
print(lever.state) 
# True as long as lever exists in timberborn

# Set a lever color
api.set_color("Lever 1", "#ffffff") # Sets to white using hex
api.set_color("Lever 1", "ff0000") # Sets to red
# Both formats are accepted

# List all levers
print(api.list_levers())

# Get adapter state
adapter = api.get_adapter("Adapter 1")
print(adapter.state)

# List all adapters
print(api.list_adapters())
```

### Listeners

```python
# Register a lever listener
def my_listener(lever_name, current_state, prev_state):
    print(f"{lever_name} changed from {prev_state} to {current_state}")

# The first time this is called, prev_state will be None, only happens once.
# This is due to there not being a previous state at that point. 
# If you want to disable this, you can do:  if prev_state is not None:

api.register_lever_listener("Lever 1", my_listener)

# Manually check for changes
api.check_lever_listeners()

# Or activate automatic loop for (in this case) 10 ticks. (Only for lever listeners)
api.activate_lever_listener_loop(
    ms_per_tick=2000, 
    exit_condition=lambda ticks: ticks > 10
    )

# You can also use a Config object when creating 'api' with attribute 'start_lever_thread=True' to start
# a thread with the lever listener loop in the background. Read TimberbornAPI.Config.__doc__ for more info.

# Register an adapter listener running on Flask server:
def adapter_listener(adapter_name, current_state, prev_state):
    print(f"{adapter_name} changed from {prev_state} to {current_state}")

api.register_adapter_listener("Adapter 1", adapter_listener)
# The adapter listener runs whenever Timberborn sends adapter changes,
# turn on the checkboxes in the adapter window.

# You can turn this off with a Config object at initialization, with 'start_adapter_server=False'.
```

### Logic Gates

Logic gates can be used to simulate the relay logic from [**Timberborn**](https://store.steampowered.com/app/1284200/Timberborn/). This allows for easy, simple to update complex logic. More thorough examples can be found in the [*Examples*](https://github.com/Joh3BL/timberborn-api/tree/main/examples) folder.

```python
from timberborn_api import TimberbornAPI

api = TimberbornAPI()

# Turns off 'Lever 1' when 'Adapter 1' is off
def turn_off_lever_1(name, current_state, prev_state):
    api.set_lever(
        "Lever 1", 
        api.and_("Adapter 1", api.L("Lever 1"))  
        )
# Strings are auto-interpreted as Adapters, recomend api.A(...) for clarity

api.register_adapter_listener("adapter 1", turn_off_lever_1)

# Calls all adapter listeners with prev_state, and new state, usually with prev_state as None
api.initialize_adapter_prev_states()

# Check NOR for 'Adapter 2' and 'Lever 2' state
print(api.or_(*api.not_( # Reverts all inputs, simulates NOR gate
    api.A("Adapter 2"), api.L("Lever 2")
    )))
```

The logic gate functions accept a **ConditionItem**, which is either a *boolean* (`True/False`), *string* (`"adapter_name"`), *Lever object* (`api.L("lever_name")`) or *Adapter object (`api.A("adapter_name")`). All adapters and levers are freshly evaluated using `get_lever` or `get_adapter`.

`not_` returns **list** if *multiple args*, **boolean** if *single arg*. Use <b>*</b>api.not_(...) to unpack for gates like **NAND**/**NOR**.<!-- markdownlint-disable-line MD033 -->

### OOP

You can *(with the latest version)* use Object Oriented Programming with the levers. This means that you access the state *or spring_return* of a `Lever`/`Adapter` using `.state`. You can also use some OOP to access functions, like:

```python
#TODO: Add stuff here
```

## API Reference

All methods are available with the `TimberbornAPI` class.
Use `TimberbornAPI.methods()` to list all public methods, or use **docstrings** *(.\_\_doc\_\_)* on a method to access a description in detail on what it does. You should also be able to use `help(TimberbornAPI)` to access all the docstrings at once.

### TimberbornAPI Methods

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
- `initialize_adapter_prev_states()`
- `not_(*args)`
- `and_(*args)`
- `or_(*args)`
- `xor_(*args)`

For the logic gates, you need to use the wrappers, `api.L()` & `api.A()`, and they work the same as the objects created after *get_lever*/*adapter* or *list_lever*/*adapter* is used.

### Lever and Adapter object methods

Lever and adapter objects can both be created using the wrappers - `api.L()` & `api.A()` - and by using `api.get_lever`/`api.get_adapter`. The levers contain a *name* property, a settable *state* property and a regular spring_return property, that can only be accessed.

**Example code:**

```python
from timberborn_api import TimberbornAPI

api = TimberbornAPI()

# Initialize objects with 'name' attribute
lever = api.L("lever 1")
adapter = api.A("adapter 1")

# Perform logic
if api.and_(lever, adapter):
    print("Both are on!")

# Turn on lever
lever.switch_on()

# Turn off lever
lever.switch_off()

# Toggle lever
lever.toggle()

# Set state to boolean
lever.state = adapter.state

# Set color of lever to white
lever.set_color("#ffffff")

# Access attributes
print(lever.state)
print(lever.spring_return)
print(adapter.state)
```

### Examples

If you have any other questions to how this works or how it can be used,  
please refer to the [*Examples*](https://github.com/Joh3BL/timberborn-api/tree/main/examples).
The docstrings also have notes on how they are intended to be used.
If something isn't provided, please open an [**Issue**](https://github.com/Joh3BL/timberborn-api/issues).

## Configuration

You usually access the API using `api = TimberbornAPI()`. All examples will also do this. To configure it, you use `config = TimberbornAPI.Config(...)`, and then `TimberbornAPI(config)`.
You can use these **Config** arguments:

- ***base_url*** (str): URL of your Timberborn API server (default: `http://localhost:8080/api`)
- ***adapter_listener_port*** (int): Port for adapter calls (default: `8081`)
- ***cache_ttl*** (float): Cache *Time To Live* in seconds (default: `8`). Used for get_lever/get_adapter
- ***on_any_change*** (callable): Optional global callback when any adapter changes
- ***start_adapter_server*** (bool): Starts the adapter listener server. (default: `True`)
- ***start_lever_thread*** (bool): Starts a separate thread that uses a lever listener loop(default: `False`)
- ***lever_thread_interval_ms*** (float): Amount of ms between ticks in lever thread (default: `5000`). Does the same thing as ms_per_tick in `activate_lever_listener_loop()`. Does nothing if `start_lever_thread` isn't **True**.

## Contributing

Contributions are welcome!

If you find a *bug* or have a *feature request*,
please open an [**Issue**](https://github.com/Joh3BL/timberborn-api/issues), and label it as *enhancement*.

If you'd like to contribute code:

1. Fork the repository
2. Create a branch
3. Submit a [**Pull Request**](https://github.com/Joh3BL/timberborn-api/pulls)

If that is too complicated, or it's just a simple function add, you can add it as an issue labeled *enhancement*.

## License

This project is licensed under the MIT License. See the [**LICENCE**](https://github.com/Joh3BL/timberborn-api/blob/main/LICENSE) file for more information.
