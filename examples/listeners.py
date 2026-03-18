# Many ways to use listeners, here are some examples
from timberborn_api import TimberbornAPI, A


# Listen to all adapter state changes
def all_adapter_and_lever_listener(adapter_name, current_state, prev_state):
    print(f"Adapter {adapter_name} changed from {prev_state} to {current_state}")
    
api = TimberbornAPI(on_any_change=all_adapter_and_lever_listener) # Listen to all changes


# Listen to specific adapter state changes
def my_listener(adapter_name, current_state, prev_state):
    print(f"Adapter {adapter_name} changed from {prev_state} to {current_state}")

api.register_adapter_listener("adapter 1", my_listener)

# Register same listener to multiple adapters
api.register_adapter_listener("adapter 2", my_listener)
api.register_adapter_listener("adapter 3", my_listener)
# This now listenes to adapters 1, 2 and 3.


# Define a listener that updates a lever based on an adapter state change
# Can be used to recreate logic, like an and gate. 
def lever_adapter_listener(adapter_name, current_state, prev_state):
    and_adapter_1_state = None
    and_adapter_2_state = None
    if adapter_name == "and adapter 1":
        and_adapter_1_state = current_state
        and_adapter_2_state = api.get_adapter("and adapter 2").state
    else:
        and_adapter_1_state = api.get_adapter("and adapter 1").state
        and_adapter_2_state = current_state
    
    api.set_lever("and lever", and_adapter_1_state and and_adapter_2_state)
    """ Can also be recreated like this, using logic functions:
    api.set_lever("and lever", api.and_(A("adapter 1"), A("adapter 2")))
    """

api.register_adapter_listener("and adapter 1", lever_adapter_listener)
api.register_adapter_listener("and adapter 2", lever_adapter_listener)

# Will now update state of "and lever" whenever the state of 
# "and adapter 1" or "and adapter 2" changes.


# Interruption listeners, stop the listener loop when some condition is met.
def interrupt_listener(name, current_state, prev_state):
    print(f"{name} changed from {prev_state} to {current_state}")
    raise KeyboardInterrupt # Interrupts the listener loop

# This example uses lever listeners, as adapter doesn't have a loop,
# and instead uses a seperate thread. This means that the main thread can still be used.
api.register_lever_listener("interrupt lever", interrupt_listener)

# Starts listening to changes, will stop when KeyboardInterrupt is raised.
api.activate_lever_listener_loop()

print("Continued normally!")


# You can also create a seperate thread for the listener loop,
# so that it doesn't block the main thread.

config = TimberbornAPI.Config(start_lever_thread=True, start_adapter_server=False)
api2 = TimberbornAPI(config)

# Only lever thread runs in api2 now.