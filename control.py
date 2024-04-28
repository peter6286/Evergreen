import lib8relind

# Set the parameters for your test
stack_level = 0  # Adjust this based on your jumper settings
relay_number = 5  # We know we're using relay 5

# Turn on the relay
lib8relind.set(stack_level, relay_number, 1)

# Wait a bit to see the action
import time
time.sleep(5)  # 5 seconds delay

# Turn off the relay
lib8relind.set(stack_level, relay_number, 0)
