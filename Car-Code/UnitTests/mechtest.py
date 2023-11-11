"""This micropython program makes the motor1 and motor2
move in forward and backward directions."""

from machine import Pin, PWM
import time
from L298N_motor import L298N

led= machine.Pin('LED', machine.Pin.OUT)
led.on()


BACK_LEFT_EN = 5
BACK_LEFT_IN1 = 3
BACK_LEFT_IN2 = 4

BACK_RIGHT_EN = 0
BACK_RIGHT_IN1 = 1
BACK_RIGHT_IN2 = 2

FRONT_LEFT_EN = 28
FRONT_LEFT_IN1 = 27
FRONT_LEFT_IN2 = 26

FRONT_RIGHT_EN = 20
FRONT_RIGHT_IN1 = 22
FRONT_RIGHT_IN2 = 21

# ENA.freq(150)
# ENB.freq(150)
# ENC.freq(150)
# END.freq(150)


back_right = L298N(BACK_RIGHT_EN, BACK_RIGHT_IN1, BACK_RIGHT_IN2)
back_left = L298N(BACK_LEFT_EN, BACK_LEFT_IN1, BACK_LEFT_IN2)
front_right = L298N(FRONT_RIGHT_EN, FRONT_RIGHT_IN1, FRONT_RIGHT_IN2)
front_left = L298N(FRONT_LEFT_EN, FRONT_LEFT_IN1, FRONT_LEFT_IN2)

back_right.forward()

speedPerc = 0.0
while True:
   
    back_right.setSpeedPerc(speedPerc)
    print("Current Percentage: ", speedPerc, "Current DC: ", back_right.getSpeed())
    
    time.sleep(2)
    
    speedPerc+=0.1




