import bluetooth, ustruct
from micropython import const
from utime import sleep_ms
import machine
import time
import utime
#import asyncio
from machine import PWM, Pin

trigger = Pin(15, Pin.OUT)
echo = Pin(14, Pin.IN)

def ultra():
   signaloff = 0
   signalon = 0
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
   print(distance)
   return distance

_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)

#Set the server address (replace with the actual address)
serverAddress = bytes(b'(\xcd\xc1\x0bV\x01')

#Event handler function
def bt_irq(event, data):
    global receivedString, dataReceivedFlag
    if event == _IRQ_SCAN_RESULT:
        # A single scan result.
        addr_type, addr, adv_type, rssi, adv_data = data
        address = bytes(addr)
        if address == serverAddress and not dataReceivedFlag:
            receivedString = str(adv_data, 'utf-8')  # Convert bytes to a UTF-8 string
            #receivedString = adv_data
            dataReceivedFlag = True
    elif event == _IRQ_SCAN_DONE:
        print('Scan finished.')

ble = bluetooth.BLE()
ble.active(True)
ble.irq(bt_irq)

scanDuration_ms = 100000  # Specify how long the scanning should take
interval_us = 15000
window_us = 15000  # The same window as interval, means continuous scan
active = False  # Do not care for a reply for a scan from the transmitter

receivedString = ""
dataReceivedFlag = False
ble.gap_scan(scanDuration_ms, interval_us, window_us, active)
advertisingInterval_us = int(1e6) # 1 second interval - just set as larger than the loop iteration duration, see below
loopIterationDuration_ms = 1000

buffer = []


while True:
    dist = ultra()
    advertisedData = ustruct.pack('<f', 0)
    ble.gap_advertise(advertisingInterval_us,adv_data=advertisedData, connectable=False) #not connectable because this is just to send the data
    
    if dataReceivedFlag:
        print(receivedString)
        dataReceivedFlag = False
    sleep_ms(loopIterationDuration_ms)
