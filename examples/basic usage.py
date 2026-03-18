# Basic way to use the library
from timberborn_api import TimberbornAPI

api = TimberbornAPI()

# Set lever state
api.set_lever("Lever 1", True)

# Get lever state
lever = api.get_lever("Lever 1")
print(lever.state) 
# True as long as lever exists in timberborn

# Set a lever color
api.set_color("Lever 1", "#ffffff")  # Sets to white using hex

# List all levers
print(api.list_levers())

# Get adapter state
adapter = api.get_adapter("Adapter 1")
print(adapter.state)

# List all adapters
print(api.list_adapters())