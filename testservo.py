import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
servo_control_pin = 4
pump_control_pin = 23
pump_override_pin = 27
pumpstate = "Off"
GPIO.setup(servo_control_pin, GPIO.OUT)
GPIO.setup(pump_control_pin, GPIO.OUT)
GPIO.setup(pump_override_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
p = GPIO.PWM(servo_control_pin, 50)
p.start(0)
angle = 0


def SetAngle(angle):
    #TODO verify all the math here
    duty = angle / 18 + 2
    GPIO.output(servo_control_pin, True)
    p.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(servo_control_pin, False)
    p.ChangeDutyCycle(0)

while True:
    input_state = GPIO.input(pump_override_pin)
    if input_state == False:
        print('Button Pressed')
        sleep(0.5)
        SetAngle(angle)
        if angle == 0:
            angle == 90