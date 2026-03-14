# Logic gate examples.
# Can be used with listeners to create logic gates, or just for checking conditions in your code.

# Make sure to import L and A as Lever and Adaptor wrappers
from timberborn_api import TimberbornAPI, L, A

api = TimberbornAPI()

# Example of using and, or and not in code
if api.and_(L("and lever 1"), L("and lever 2")):
    print("Both levers are on")

# Explicit and implicit adaptors
if api.or_(L("or lever 1"), A("or adaptor 2"), "or adaptor 3"):
    print("At least one http relay is on")

def adaptor_listener(adaptor_name, current_state, _):
    if api.not_(current_state): # If adaptor is off
        print(f"{adaptor_name} turned off")
        raise KeyboardInterrupt # Stops the listener_loop, progresses normally

api.register_listener("not adaptor", adaptor_listener)

# Starts listening to changes, will stop when KeyboardInterrupt is raised
api.activate_listener_loop()

print("Continued normally")