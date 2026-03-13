# Timberborn API

Python client for the Timberborn HTTP API.

## Features
- Control levers
- Read adaptors
- Listener system for state changes
- Fast caching

## Example

'''python
from timberborn_api import TimberbornAPI

api = TimberbornAPI()

api.set_lever("Lever 1", True)

lever = api.get_lever("Lever 1")
print(lever["state"])