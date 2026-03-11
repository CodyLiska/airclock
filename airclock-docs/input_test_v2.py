from gpiozero import RotaryEncoder, Button
from signal import pause

# Your wiring
# S1 -> GPIO17
# S2 -> GPIO27
# Key -> GPIO22

enc = RotaryEncoder(a=17, b=27, max_steps=0)  # max_steps=0 = no limit
select = Button(22, pull_up=True, bounce_time=0.05)  # 50ms debounce

# Track steps so we only print when it actually changes
last_steps = enc.steps

def report():
    global last_steps
    steps = enc.steps
    if steps != last_steps:
        direction = "Clockwise" if steps > last_steps else "Counterclockwise"
        print(direction, "steps:", steps)
        last_steps = steps

# gpiozero doesn't always fire per detent reliably across all encoder modules,
# so we poll at a light rate; this is very stable for menu navigation.
import time
print("Rotate encoder / press button. CTRL+C to quit.")
try:
    while True:
        report()
        if select.is_pressed:
            # only print once per press
            print("SELECT pressed")
            while select.is_pressed:
                time.sleep(0.01)
        time.sleep(0.005)
except KeyboardInterrupt:
    pass
