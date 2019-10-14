import RPi.GPIO as GPIO
import board
import busio
import adafruit_ssd1306
import digitalio
from PIL import Image, ImageDraw, ImageFont

i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
oled.fill(0)
oled.show()
font = ImageFont.load_default()
image = Image.new('1', (oled.width, oled.height))
draw = ImageDraw.Draw(image)

def updateScreen(message, pumpstate):
    text = message
    (font_width, font_height) = font.getsize(text)
    draw.text((oled.width//2 - font_width//2, oled.height//2 - font_height//2),
    text, font=font, fill=255)

updateScreen("Hello World", "On")