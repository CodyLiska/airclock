from gpiozero import DigitalOutputDevice
from luma.core.interface.serial import spi
from luma.lcd.device import ili9341
from luma.core.render import canvas
from PIL import ImageFont

# Backlight is wired to GPIO26, not always-on 3.3V — must be driven high.
backlight = DigitalOutputDevice(26, initial_value=True)

serial = spi(port=0, device=0, gpio_DC=25, gpio_RST=18, bus_speed_hz=4000000)

device = ili9341(serial, width=320, height=240, rotate=1)

font = ImageFont.load_default()

with canvas(device) as draw:
    draw.text((40, 100), "Display Works!", fill="white", font=font)

input("Press Enter to exit...")
