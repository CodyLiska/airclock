import board
import digitalio
from adafruit_rgb_display import ili9486
from PIL import Image

backlight = digitalio.DigitalInOut(board.D26)
backlight.switch_to_output()
backlight.value = True

cs_pin = digitalio.DigitalInOut(board.D8)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D18)

spi = board.SPI()

disp = ili9486.ILI9486(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=4000000,
    width=480,
    height=320,
)

image = Image.new("RGB", (480, 320), (255, 0, 0))
disp.image(image)
