import time
from gpiozero import RotaryEncoder, Button

# Encoder wiring
enc = RotaryEncoder(a=17, b=27, max_steps=0)
select = Button(22, pull_up=True, bounce_time=0.08)

# Extra buttons
back = Button(23, pull_up=True, bounce_time=0.08)
snooze = Button(5, pull_up=True, bounce_time=0.08)

last_steps = enc.steps
last_select = False
last_back = False
last_snooze = False

print("Rotate encoder / press SELECT / press BACK / press SNOOZE. CTRL+C to quit.")

try:
    while True:
        # Encoder rotation (stable)
        steps = enc.steps
        if steps != last_steps:
            direction = "Clockwise" if steps > last_steps else "Counterclockwise"
            print(f"{direction} steps: {steps}")
            last_steps = steps

        # Edge-detect buttons so they print once per press
        sel_now = select.is_pressed
        if sel_now and not last_select:
            print("SELECT pressed")
        last_select = sel_now

        back_now = back.is_pressed
        if back_now and not last_back:
            print("BACK pressed")
        last_back = back_now

        snooze_now = snooze.is_pressed
        if snooze_now and not last_snooze:
            print("SNOOZE pressed")
        last_snooze = snooze_now

        time.sleep(0.005)

except KeyboardInterrupt:
    pass
