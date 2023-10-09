import bluetooth, ustruct
from micropython import const
from utime import sleep_ms
import machine
import time, utime
from machine import PWM, Pin

# trigger = Pin(15, Pin.OUT)
# echo = Pin(14, Pin.IN)

advertisingInterval_us = int(1e6) # 1 second interval - just set as larger than the loop iteration duration, see below
loopIterationDuration_ms = 1000

# def ultra():
#    trigger.low()
#    utime.sleep_us(2)
#    trigger.high()
#    utime.sleep_us(5)
#    trigger.low()
#    
#    signaloff = utime.ticks_us()
#    signalon = utime.ticks_us()
#    while echo.value() == 0:
#        signaloff = utime.ticks_us()
#        
#    while echo.value() == 1:
#        signalon = utime.ticks_us()
#        
#    timepassed = signalon - signaloff
#    distance = (timepassed * 0.0343) / 2
#    if distance < 100:
#        return 10
#    elif distance > 100:
#        return 20
#    else:
#        return 30

led = machine.Pin('LED', machine.Pin.OUT)
led.on()

_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)

# Set the server address (replace with the actual address)
serverAddress = bytes(b'(\xcd\xc1\x0bV\x01')

# Event handler function
def bt_irq(event, data):
    global receivedNumber, dataReceivedFlag
    if event == _IRQ_SCAN_RESULT:
        # A single scan result.
        addr_type, addr, adv_type, rssi, adv_data = data
        address = bytes(addr)
        if address == serverAddress and not dataReceivedFlag:
            receivedNumber = ustruct.unpack('<i', adv_data)[0]  # Unpack integer
            dataReceivedFlag = True
    elif event == _IRQ_SCAN_DONE:
        print('Scan finished.')

ble = bluetooth.BLE()
ble.active(True)
ble.irq(bt_irq)

scanDuration_ms = 1000000  # Specify how long the scanning should take
interval_us = 15000
window_us = 15000  # The same window as interval, means continuous scan
active = False  # Do not care for a reply for a scan from the transmitter

receivedNumber = 0
dataReceivedFlag = False
ble.gap_scan(scanDuration_ms, interval_us, window_us, active)

ENA = PWM(Pin(0))        
IN1 = Pin(1, Pin.OUT)         
IN2 = Pin(2, Pin.OUT)
IN3 = Pin(3, Pin.OUT)
IN4 = Pin(4, Pin.OUT)
ENB = PWM(Pin(5))
ENA.freq(150)
ENB.freq(150)
ENA.duty_u16(65535)
ENB.duty_u16(65535)

while True:
    #advertisedData = ustruct.pack('<i', ultra())
    #ble.gap_advertise(advertisingInterval_us,adv_data=advertisedData, connectable=False)
    if dataReceivedFlag:
        print(receivedNumber)
        if receivedNumber == 0: # Stop
            IN1.low()
            IN2.low()
            IN3.low()
            IN4.low()
        elif receivedNumber == 1:# Forward
            IN1.low()
            IN2.high()
            IN3.high()
            IN4.low()
        elif receivedNumber == 2: # Backward
            IN1.high()
            IN2.low()
            IN3.low()
            IN4.high()
        elif receivedNumber == 3: # Right
            IN3.low()
            IN4.high()
            IN1.low()
            IN2.high()
        elif receivedNumber == 4: # Left
            IN3.high()
            IN4.low()
            IN1.high()
            IN2.low()
        dataReceivedFlag = False