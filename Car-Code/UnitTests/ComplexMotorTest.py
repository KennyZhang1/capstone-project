"""This micropython program makes the motor1 and motor2
move in forward and backward directions."""

from machine import Pin, PWM
from L298N_motor import L298N
import time

ENA = PWM(Pin(0))        
IN1 = Pin(1, Pin.OUT)         
IN2 = Pin(2, Pin.OUT)
IN3 = Pin(3, Pin.OUT)
IN4 = Pin(4, Pin.OUT)
ENB = PWM(Pin(5))

motor1 = L298N(ENA, IN1, IN2)     #create a motor1 object
motor2 = L298N(ENB, IN3, IN4)     #create a motor2 object

motor1.setSpeed(30000)            #set the speed of motor1. Speed value varies from 25000 to 65534
motor2.setSpeed(25000)            #set the speed of motor2. Speed value varies from 25000 to 65534

while True:
    motor1.forward()      #run motor1 forward
    motor2.forward()      #run motor2 forward
    time.sleep(5)         #wait for 5 seconds
    motor1.backward()     #run motor1 backward
    motor2.backward()     #run motor1 backward
    time.sleep(5)         #run motor2 backward