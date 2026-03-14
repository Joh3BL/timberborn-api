# Logic gate examples.
# Can be used with listeners to create logic gates, or just for checking conditions in your code.

# Make sure to import L and A as Lever and Adapter wrappers
from timberborn_api import TimberbornAPI, L, A

api = TimberbornAPI()

# Example of using and, or and not in code
if api.and_(L("and lever 1"), L("and lever 2")):
    print("Both levers are on")

# Explicit and implicit adapters
if api.or_(L("or lever 1"), A("or adapter 2"), "or adapter 3"):
    print("At least one http relay is on")

def adapter_listener(adapter_name, current_state, _):
    if api.not_(current_state): # If adapter is off
        print(f"{adapter_name} turned off")
        raise KeyboardInterrupt # Stops the listener_loop, progresses normally

api.register_listener("not adapter", adapter_listener)

# Starts listening to changes, will stop when KeyboardInterrupt is raised
api.activate_listener_loop()

print("Continued normally")