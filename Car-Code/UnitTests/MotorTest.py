"""This micropython program makes the motor1 and motor2
move in forward and backward directions."""

from machine import Pin, PWM
import time 

# ENA = PWM(Pin(0))
ENA = Pin(0, Pin.OUT)
IN1 = Pin(1, Pin.OUT)         
IN2 = Pin(2, Pin.OUT)
IN3 = Pin(3, Pin.OUT)
IN4 = Pin(4, Pin.OUT)
ENB = Pin(5, Pin.OUT)
# ENB = PWM(Pin(5))

# ENA.freq(150)
# ENB.freq(150)

while True:
    
#     ENA.duty_u16(40000)
    ENA.high()
    IN1.high()
    IN2.low()
    
#     ENB.duty_u16(40000)
    ENB.high()
    IN3.high()
    IN4.low()
    #time.sleep(5)