import board
import busio
import adafruit_ssd1306
import digitalio
from PIL import Image, ImageDraw, ImageFont

i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
oled.fill(255)
oled.show()
font = ImageFont.truetype("PTM55FT.ttf", 12, encoding = "unic")
image = Image.new('1', (oled.width, oled.height))
draw = ImageDraw.Draw(image)

def updateScreen(message, pumpstate):
    text = message
    textlinetwo = "Pump is " + pumpstate
    (font_width, font_height) = font.getsize(text)
    draw.text((oled.width//2 - font_width//2, oled.height//2 - font_height),text, font=font, fill=255)
    draw.text((oled.width//2 - font_width//2, oled.height//2 + font_height//4),textlinetwo, font=font, fill=255)
    oled.image(image)
    oled.show()

updateScreen("Hello World", "On")