# Many ways to use listeners, here are some examples
from timberborn_api import TimberbornAPI

# Listen to all adaptor state changes
def all_adaptor_listener(adaptor_name, current_state, prev_state):
    print(f"Adaptor {adaptor_name} changed from {prev_state} to {current_state}")
    
api = TimberbornAPI(on_any_change=all_adaptor_listener) # Listen to all adaptor changes

# Listen to specific adaptor state changes
def my_listener(adaptor_name, current_state, prev_state):
    print(f"Adaptor {adaptor_name} changed from {prev_state} to {current_state}")

api.register_listener("adaptor 1", my_listener)

# Register same listener to multiple adaptors
api.register_listener("adaptor 2", my_listener)
api.register_listener("adaptor 3", my_listener)

# This now listenes to adaptors 1, 2 and 3.

# Define a listener that updates a lever based on an adaptor state change
# Can be used to recreate logic, like an and gate. 
def lever_adaptor_listener(adaptor_name, current_state, prev_state):
    and_adaptor_1_state = None
    and_adaptor_2_state = None
    if adaptor_name == "and adaptor 1":
        and_adaptor_1_state = current_state
        and_adaptor_2_state = api.get_adaptor("and adaptor 2")['state']
    else:
        and_adaptor_1_state = api.get_adaptor("and adaptor 1")['state']
        and_adaptor_2_state = current_state
    
    api.set_lever("and lever", and_adaptor_1_state and and_adaptor_2_state)

api.register_listener("and adaptor 1", lever_adaptor_listener)
api.register_listener("and adaptor 2", lever_adaptor_listener)

# Will now update state of "and lever" whenever the state of 
# "and adaptor 1" or "and adaptor 2" changes.