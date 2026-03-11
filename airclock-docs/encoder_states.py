import RPi.GPIO as GPIO
import time

S1 = 17
S2 = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(S1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(S2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Watching S1,S2 states. Rotate slowly. CTRL+C to quit.")
last = (GPIO.input(S1), GPIO.input(S2))
print("Initial:", last)

try:
    while True:
        cur = (GPIO.input(S1), GPIO.input(S2))
        if cur != last:
            print(cur)
            last = cur
        time.sleep(0.001)
except KeyboardInterrupt:
    GPIO.cleanup()
