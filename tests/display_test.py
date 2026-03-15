from luma.core.interface.serial import spi
from luma.lcd.device import ili9341
from luma.core.render import canvas
from PIL import ImageFont

serial = spi(port=0, device=0, gpio_DC=25, gpio_RST=24)

device = ili9341(serial, width=320, height=240, rotate=1)

font = ImageFont.load_default()

with canvas(device) as draw:
    draw.text((40, 100), "Display Works!", fill="white", font=font)

input("Press Enter to exit...")
