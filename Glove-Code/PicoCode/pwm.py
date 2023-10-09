import machine
import time
from machine import PWM, Pin

led= machine.Pin('LED', machine.Pin.OUT)

# while (True):
#     led.on()
#     time.sleep(0.5)
#     led.off()
#     time.sleep(0.5)
led.on()
# po = machine.Pin(0, machine.Pin.OUT)
# po.on()
pwm = PWM(Pin(2))
pwm.freq(8)
#pwm.duty_u16(20000)
#

while True:
    for i in range(20000, 65535, 5):
        pwm.duty_u16(i)
        print(i/65535*100)
        time.sleep(0.01)