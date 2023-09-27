import ustruct, bluetooth
from utime import sleep_ms
import utime
from micropython import const
from machine import Pin

led = machine.Pin('LED', machine.Pin.OUT)
led.on()
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)

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
    #distance = (timepassed * 0.0343) / 2
    return timepassed

def bt_irq(event, data):
    global receivedString, dataReceivedFlag
    if event == _IRQ_SCAN_RESULT:
        # A single scan result.
        addr_type, addr, adv_type, rssi, adv_data = data
        address = bytes(addr)
        if address == serverAddress and not dataReceivedFlag:
            receivedString = str(adv_data, 'utf-8')  # Convert bytes to a UTF-8 string
            dataReceivedFlag = True
    elif event == _IRQ_SCAN_DONE:
        print('Scan finished.')
   
ble = bluetooth.BLE()
ble.active(True)
ble.irq(bt_irq)
# print(bytes(ble.config('mac')[1])) # get the address of your transmitter to put into the receiver code

advertisingInterval_us = int(1e3) # 1 second interval - just set as larger than the loop iteration duration, see below
loopIterationDuration_ms = 1000
serverAddress = bytes(b'(\xcd\xc1\x0bT\xa7')

scanDuration_ms = 100000  # Specify how long the scanning should take
interval_us = 15000
window_us = 15000  # The same window as interval, means continuous scan
active = False  # Do not care for a reply for a scan from the transmitter

receivedString = 0
dataReceivedFlag = False
ble.gap_scan(scanDuration_ms, interval_us, window_us, active)


counter = 0
while True:
        advertisedData = ustruct.pack('<i',counter%3)
        ble.gap_advertise(advertisingInterval_us,adv_data=advertisedData, connectable=False) #not connectable because this is just to send the data
        #print(receivedString)
        print(advertisedData)
        counter = counter + 1
        sleep_ms(2000)

    




