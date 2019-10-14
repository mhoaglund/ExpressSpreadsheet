from multiprocessing import Process
import RPi.GPIO as GPIO
import board
import busio
import adafruit_ssd1306
import digitalio
from PIL import Image, ImageDraw, ImageFont
from time import sleep

class OutputManager(Process):
    def __init__(self, _settings):
        super(OutputManager, self).__init__()
        GPIO.setmode(GPIO.BCM)
        self.cont = True
        self.trigger_queue = _settings.trigger_queue
        self.logging_queue = _settings.logging_queue
        self.servo_control_pin = _settings.pin
        self.pump_control_pin = _settings.pump
        self.pumpstate = "Off"
        GPIO.setup(self.servo_control_pin, GPIO.OUT)
        GPIO.setup(self.pump_control_pin, GPIO.OUT)
        self.p = GPIO.PWM(self.servo_control_pin, 50)
        self.p.start(0)
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.oled = adafruit_ssd1306.SSD1306_I2C(128, 32, self.i2c)
        self.oled.fill(0)
        self.oled.show()
        self.font = ImageFont.load_default()
        image = Image.new('1', (self.oled.width, self.oled.height))
        self.draw = ImageDraw.Draw(image)
    
    def run(self):
        while self.cont:
            while not self.trigger_queue.empty():
                latest = self.trigger_queue.get()
                if latest.reading is not None:
                    self.updateServo(latest.reading)
                    self.updateScreen(latest.date, self.pumpstate)
                if latest.reading is None and latest.state is not None:
                    #TODO turn pump on or off bsaed on latest.state flag
                    self.pumpstate = latest.state
                    self.updateScreen("---", latest.state)
                    self.updatePump(latest.state)
                    continue
                sleep(4)

    def updateServo(self, reading):
        #TODO compute an angle from the reading based on range provided
        self.SetAngle(reading/2)

    def updatePump(self, state):
        if state == "On":
            GPIO.output(self.pump_control_pin, GPIO.HIGH)
        if state == "Off":
            GPIO.output(self.pump_control_pin, GPIO.LOW)
        self.logging_queue.put("Pump State Changed")

    def updateScreen(self, message, pumpstate):
        text = message
        (font_width, font_height) = self.font.getsize(text)
        self.draw.text((self.oled.width//2 - font_width//2, self.oled.height//2 - font_height//2),
        text, font=self.font, fill=255)

    def SetAngle(self, angle):
        #TODO verify all the math here
        duty = angle / 18 + 2
        GPIO.output(self.servo_control_pin, True)
        self.p.ChangeDutyCycle(duty)
        sleep(1)
        GPIO.output(self.servo_control_pin, False)
        self.p.ChangeDutyCycle(0)

    def stop(self):
        """Stop method called from parent"""
        self.cont = False