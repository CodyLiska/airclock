from gpiozero import RotaryEncoder, Button
from signal import pause

encoder = RotaryEncoder(17, 27, wrap=True)
encoder.when_rotated_clockwise = lambda: print("Clockwise")
encoder.when_rotated_counter_clockwise = lambda: print("Counter Clockwise")

select = Button(22)
back = Button(23)
snooze = Button(5)

select.when_pressed = lambda: print("SELECT pressed")
back.when_pressed = lambda: print("BACK pressed")
snooze.when_pressed = lambda: print("SNOOZE pressed")

print("Input test running...")
pause()
