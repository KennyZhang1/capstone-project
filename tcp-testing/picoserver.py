import network
import socket
import time
import random
from machine import Pin
import utime

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
   ret_val = "The distance from object is "+str(distance)+" cm"
   return ret_val

trigger = Pin(15, Pin.OUT)
echo = Pin(14, Pin.IN)
# basic TCP server for Pico W

# WIFI credentials
ssid = "Kenny's Galaxy S10"
password = "pomk0499"

# connect to a network using network library
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
       
# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)
cl, addr = s.accept()
print('CLIENT connected from: ', addr)

print('listening on: ', addr)

# Listen for connections
while True:
    ultrasonic_data = ultra()
    try:
        request = cl.recv(1024)
        message = request.decode("utf-8")
        print(message)
        
        output_data = ultrasonic_data.encode("utf-8")
        cl.send(output_data)
        

    except OSError as e:
        cl.close()
        print('connection closed')
