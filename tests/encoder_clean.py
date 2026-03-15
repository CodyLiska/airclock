import RPi.GPIO as GPIO
import time

S1 = 17   # Encoder A
S2 = 27   # Encoder B

GPIO.setmode(GPIO.BCM)
GPIO.setup(S1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(S2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

position = 0
last_time = 0.0
DEBOUNCE_SEC = 0.003  # 3ms; increase to 0.005–0.01 if still noisy

def on_s1_falling(channel):
    global position, last_time
    now = time.time()
    if now - last_time < DEBOUNCE_SEC:
        return
    last_time = now

    b = GPIO.input(S2)
    if b == 1:
        position += 1
        print("Clockwise", position)
    else:
        position -= 1
        print("Counterclockwise", position)

GPIO.add_event_detect(S1, GPIO.FALLING, callback=on_s1_falling, bouncetime=2)

print("Rotate encoder. CTRL+C to quit.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
