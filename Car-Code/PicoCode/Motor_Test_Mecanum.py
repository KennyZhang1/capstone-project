"""This micropython program makes the motor1 and motor2
move in forward and backward directions."""

from machine import Pin, PWM
import time

# ENA = PWM(Pin(0))        
# IN1 = Pin(1, Pin.OUT)         
# IN2 = Pin(2, Pin.OUT)
# IN3 = Pin(3, Pin.OUT)
# IN4 = Pin(4, Pin.OUT)
# ENB = PWM(Pin(5))
# ENA.freq(150)
# ENB.freq(150)
# ENA.duty_u16(10000)
# ENB.duty_u16(10000)

# motor pin inits
# motor pin inits
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

ENA.freq(150)
ENB.freq(150)
ENC.freq(150)
END.freq(150)

ENA.duty_u16(30000)
ENB.duty_u16(30000)
ENC.duty_u16(30000)
END.duty_u16(30000)


while True:
    IN1.high()
    IN2.low()
    IN3.high()
    IN4.low()
    IN5.low()
    IN6.high()
    IN7.low()
    IN8.high()
    time.sleep(5)
