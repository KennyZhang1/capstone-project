"""This micropython program makes the motor1 and motor2
move in forward and backward directions."""

from machine import Pin, PWM
import time
from L298N_motor import L298N

led= machine.Pin('LED', machine.Pin.OUT)
led.on()


ENA = PWM(Pin(0))
IN1 = Pin(1, Pin.OUT)         
IN2 = Pin(2, Pin.OUT)
IN3 = Pin(3, Pin.OUT)
IN4 = Pin(4, Pin.OUT)
ENB = PWM(Pin(5))
ENC = PWM(Pin(28))
IN5 = Pin(27, Pin.OUT)         
IN6 = Pin(26, Pin.OUT)
IN7 = Pin(22, Pin.OUT)
IN8 = Pin(21, Pin.OUT)
END = PWM(Pin(20))

# ENA.freq(150)
# ENB.freq(150)
# ENC.freq(150)
# END.freq(150)


back_right = L298N(ENA, IN1, IN2)
back_right.setSpeed(65535)

back_left = L298N(ENB, IN3, IN4)
back_left.setSpeed(60000)

front_right = L298N(END, IN7, IN8)
front_right.setSpeed(55000)

front_left = L298N(ENC, IN5, IN6)
front_left.setSpeed(50000)


while True:

    back_right.forward()
    back_left.backward()
    front_right.forward()
    front_left.backward()
#     ENA.duty_u16(34000)
#     ENB.duty_u16(35000)
#     ENC.duty_u16(35000)
#     END.duty_u16(34000)
#  
#     #forward
#     IN1.high()
#     IN2.low()
#     IN3.low()
#     IN4.high()
#     IN5.low()
#     IN6.high()
#     IN7.high()
#     IN8.low()
#     
    time.sleep(2)
# 
#     IN1.low()
#     IN2.high()
#     IN3.low()
#     IN4.high()
#     IN5.high()
#     IN6.low()
#     IN7.high()
#     IN8.low()
#     time.sleep(2)
    
    #strafe



