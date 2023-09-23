# resource https://www.tomshardware.com/how-to/raspberry-pi-pico-ultrasonic-sensor
from machine import Pin
import utime

trigger = Pin(15, Pin.OUT)
echo = Pin(14, Pin.IN)

def ultra():
   trigger.low()
   utime.sleep_us(2)
   trigger.high()
   utime.sleep_us(5)
   trigger.low()
   
   while echo.value() == 0:
       signaloff = utime.ticks_us()
       
   while echo.value() == 1:
       signalon = utime.ticks_us()
       
   timepassed = signalon - signaloff
   distance = (timepassed * 0.0343) / 2
   print("The distance from object is ",distance,"cm")
   
while True:
   ultra()
   #print("The distance from object is cm")
   utime.sleep(1)