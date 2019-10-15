import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
servo_control_pin = 4
pump_control_pin = 18
pumpstate = "Off"
GPIO.setup(servo_control_pin, GPIO.OUT)
GPIO.setup(pump_control_pin, GPIO.OUT)
p = GPIO.PWM(servo_control_pin, 50)
p.start(0)


def SetAngle(angle):
    #TODO verify all the math here
    duty = angle / 18 + 2
    GPIO.output(servo_control_pin, True)
    p.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(servo_control_pin, False)
    p.ChangeDutyCycle(0)

SetAngle(90)
sleep(5)
SetAngle(0)
sleep(5)
SetAngle(180)