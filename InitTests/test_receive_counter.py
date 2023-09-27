import bluetooth, ustruct
from micropython import const
from utime import sleep_ms
import machine
import time
from machine import PWM, Pin

led = machine.Pin('LED', machine.Pin.OUT)
led.on()
pwm = PWM(Pin(0))
pwm.freq(8)

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

scanDuration_ms = 100000  # Specify how long the scanning should take
interval_us = 15000
window_us = 15000  # The same window as interval, means continuous scan
active = False  # Do not care for a reply for a scan from the transmitter

receivedNumber = 0
dataReceivedFlag = False
ble.gap_scan(scanDuration_ms, interval_us, window_us, active)

while True:
    if dataReceivedFlag:
        print(receivedNumber)
        if receivedNumber == 0:
            pwm.duty_u16(0)
        elif receivedNumber == 1:
            pwm.duty_u16(10000)
        elif receivedNumber == 2:
            pwm.duty_u16(60000)
        dataReceivedFlag = False

