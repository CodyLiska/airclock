import RPi.GPIO as GPIO
import time

CLK = 17
DT = 27

GPIO.setmode(GPIO.BCM)

GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

last_clk = GPIO.input(CLK)

print("Rotate encoder...")

try:
    while True:
        clk_state = GPIO.input(CLK)

        if clk_state != last_clk:
            dt_state = GPIO.input(DT)

            if dt_state != clk_state:
                print("Clockwise")
            else:
                print("Counterclockwise")

        last_clk = clk_state
        time.sleep(0.001)

except KeyboardInterrupt:
    GPIO.cleanup()
