# Many ways to use listeners, here are some examples
from timberborn_api import TimberbornAPI

api = TimberbornAPI()

# Listen to lever state changes
def my_listener(lever_name, current_state, prev_state):
    print(f"Lever {lever_name} changed from {prev_state} to {current_state}")

api.register_listener("adaptor 1", my_listener)