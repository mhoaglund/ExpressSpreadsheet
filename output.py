from multiprocessing import Process
import RPi.GPIO as GPIO
import board
import busio
import adafruit_ssd1306
import digitalio
from PIL import Image, ImageDraw, ImageFont
from time import sleep

class HardwareController(Process):
    def __init__(self, _settings):
        super(HardwareController, self).__init__()
        GPIO.setmode(GPIO.BCM)
        self.cont = True
        self.trigger_queue = _settings.trigger_queue
        self.logging_queue = _settings.logging_queue
        self.servo_control_pin = 4
        self.pump_override_pin = 27
        self.pump_control_pin = 23
        self.pumpstate = "On"
        GPIO.setup(self.servo_control_pin, GPIO.OUT)
        GPIO.setup(self.pump_control_pin, GPIO.OUT)
        GPIO.setup(self.pump_override_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.p = GPIO.PWM(self.servo_control_pin, 50)
        self.p.start(0)
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.oled = adafruit_ssd1306.SSD1306_I2C(128, 32, self.i2c)
        self.oled.fill(0)
        self.oled.show()
        self.font = ImageFont.truetype("PTM55FT.ttf", 12, encoding = "unic")
        self.image = Image.new('1', (self.oled.width, self.oled.height))
        self.draw = ImageDraw.Draw(self.image)
        self.prev_reading = 0
        self.updatePump(self.pumpstate)
        self.logging_queue.put("Output process started...")
    
    def run(self):
        while self.cont:
            input_state = GPIO.input(self.pump_override_pin)
            if input_state == False:
                if self.pumpstate == "On":
                    self.updatePump("Off")
                else:
                    self.updatePump("On")
            sleep(1)
            while not self.trigger_queue.empty():
                latest = self.trigger_queue.get()
                self.logging_queue.put("Got data packet in output queue")
                if latest.reading is not None:
                    if latest.reading != self.prev_reading:
                        self.logging_queue.put("Updating pump servo...")
                        self.updateServo(latest.reading)
                    self.prev_reading = latest.reading
                    self.updateScreen(latest.timestamp, self.pumpstate)
                if latest.reading is None and latest.state is not None:
                    #TODO turn pump on or off bsaed on latest.state flag
                    self.pumpstate = latest.state
                    self.updateScreen("---", latest.state)
                    self.updatePump(latest.state)
                    continue

    def updateServo(self, reading):
        self.SetAngle(reading)

    def updatePump(self, state):
        if state == "On":
            GPIO.output(self.pump_control_pin, GPIO.HIGH)
        if state == "Off":
            GPIO.output(self.pump_control_pin, GPIO.LOW)
        self.logging_queue.put("Pump State Changed to " + state)
        self.pumpstate = state

    def updateScreen(self, message, pumpstate):
        self.oled.fill(0)
        self.oled.show()
        self.image = Image.new('1', (self.oled.width, self.oled.height))
        self.draw = ImageDraw.Draw(self.image)
        text = message
        textlinetwo = "Pump is " + pumpstate
        (font_width, font_height) = self.font.getsize(text)
        self.draw.text((self.oled.width//2 - font_width//2, self.oled.height//2 - font_height),text, font=self.font, fill=255)
        self.draw.text((self.oled.width//2 - font_width//2, self.oled.height//2 + font_height//4),textlinetwo, font=self.font, fill=255)
        self.oled.image(self.image)
        self.oled.show()

    def SetAngle(self, angle):
        duty = int(angle) / 18 + 2
        GPIO.output(self.servo_control_pin, True)
        self.p.ChangeDutyCycle(duty)
        sleep(1)
        GPIO.output(self.servo_control_pin, False)
        self.p.ChangeDutyCycle(0)

    def stop(self):
        """Stop method called from parent"""
        self.cont = False