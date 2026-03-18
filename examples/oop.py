"""
OOP Example for TimberbornAPI

This example demonstrates:
- Using Lever and Adapter objects (OOP style)
- Reading and modifying lever states
- Using logic gates with objects
"""

from timberborn_api import TimberbornAPI

# Initialize API (default config)
api = TimberbornAPI()


# Create OOP objects

# Create Lever and Adapter objects using wrappers
lever_1 = api.L("Lever 1")
lever_2 = api.L("Lever 2")
adapter_1 = api.A("Adapter 1")
adapter_2 = api.A("Adapter 2")


# Accessing properties

# Read current states
print("Lever 1 state:", lever_1.state)
print("Lever 2 state:", lever_2.state)
print("Adapter 1 state:", adapter_1.state)
print("Adapter 2 state:", adapter_2.state)

# Lever-specific property
print("Lever 1 spring return:", lever_1.spring_return)


# Controlling levers (OOP style)

# Turn lever on
lever_2.switch_on()
print("Lever 2 turned ON:", lever_2.state)

# Turn lever off
lever_2.switch_off()
print("Lever 2 turned OFF:", lever_2.state)

# Toggle lever state
lever_2.toggle()
print("Lever 2 toggled:", lever_2.state)

# Directly assign state (uses setter internally)
lever_2.state = False
print("Lever 2 set via property:", lever_2.state)

# Set lever color (accepts "#RRGGBB" or "RRGGBB")
lever_1.set_color("#00FF00")  # green
print("Lever 1 color set to green")


# Logic gates with OOP objects

# Logic gates accept:
# - bools
# - Lever objects
# - Adapter objects
# - strings (adapter names)

# AND gate: True if all inputs are True
if api.and_(lever_1, adapter_1):
    print("Lever 1 AND Adapter 1 are ON")

# OR gate: True if any input is True
if api.or_(lever_1, adapter_2):
    print("Either Lever 1 or Adapter 2 is ON")

# NOT gate:
# - returns boolean if one argument
# - returns list if multiple arguments
print("NOT Adapter 2:", api.not_(adapter_2))

# XOR gate: True if odd number of inputs are True
print("XOR (Lever 1, Adapter 1):", api.xor_(lever_1, adapter_1))


# Example: Using logic to control a lever

# Turn Lever 1 ON only if:
# Adapter 1 is ON AND Lever 2 is ON
condition = api.and_(adapter_1, lever_2)

lever_1.state = condition
print("Lever 1 set based on condition:", lever_1.state)


# Example: NOR gate (NOT OR)

# NOR = NOT (A OR B)
# Using API:
nor_result = api.or_(*api.not_(adapter_1, lever_2))
print("NOR(Adapter 1, Lever 2):", nor_result)

# Apply NOR result to a lever
lever_1.state = nor_result
print("Lever 1 set using NOR logic:", lever_1.state)