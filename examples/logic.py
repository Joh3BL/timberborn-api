# Logic gate examples.
# Can be used with listeners to create logic gates, or just for checking conditions in your code.

# Make sure to import L and A as Lever and Adapter wrappers
from timberborn_api import TimberbornAPI

api = TimberbornAPI()

# Example of using and, or and not in code
if api.and_(api.L("and lever 1"), api.L("and lever 2")):
    print("Both levers are on")

# Explicit and implicit adapters using api.L, api.A and strings
if api.or_(api.L("or lever 1"), api.A("or adapter 2"), "or adapter 3"):
    print("At least one http relay is on")

def lever_listener(lever_name, current_state, prev_state):
    if api.not_(current_state) and prev_state is not None: # If adapter is off
        print(f"{lever_name} turned off")
        raise KeyboardInterrupt # Stops the lever_listener_loop, progresses normally
# Make sure to check for is not None, as otherwise it will always trigger the first time 

api.register_lever_listener("not adapter", lever_listener)

# Starts listening to changes, will stop when KeyboardInterrupt is raised.
# Adapter listener lives in seperate thread, and it is not useful to stop it.
api.activate_lever_listener_loop()

print("Continued normally")