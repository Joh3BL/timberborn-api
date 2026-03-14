# Basic way to use the library
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