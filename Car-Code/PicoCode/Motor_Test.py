"""This micropython program makes the motor1 and motor2
move in forward and backward directions."""

from machine import Pin, PWM
import time

ENA = PWM(Pin(0))        
IN1 = Pin(1, Pin.OUT)         
IN2 = Pin(2, Pin.OUT)
IN3 = Pin(3, Pin.OUT)
IN4 = Pin(4, Pin.OUT)
ENB = PWM(Pin(5))
ENA.freq(150)
ENB.freq(150)
ENA.duty_u16(30000)
ENB.duty_u16(30000)

while True:
    IN1.low()
    IN2.high()
    IN3.high()
    IN4.low()
    time.sleep(5)