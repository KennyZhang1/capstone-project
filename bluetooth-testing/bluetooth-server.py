import bluetooth, ustruct
from micropython import const
from utime import sleep_ms

_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)

Set the server address (replace with the actual address)
serverAddress = bytes(b'(\xcd\xc1\x0bV\x01')

Event handler function
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

scanDuration_ms = 100000  # Specify how long the scanning should take
interval_us = 15000
window_us = 15000  # The same window as interval, means continuous scan
active = False  # Do not care for a reply for a scan from the transmitter

receivedString = ""
dataReceivedFlag = False
ble.gap_scan(scanDuration_ms, interval_us, window_us, active)
advertisingInterval_us = int(1e6) # 1 second interval - just set as larger than the loop iteration duration, see below
loopIterationDuration_ms = 1000

while True:
    advertisedData = b'Hellow,world' # the integer to send as advertised data
    ble.gap_advertise(advertisingInterval_us,adv_data=advertisedData, connectable=False) #not connectable because this is just to send the data
    if dataReceivedFlag:
        print(receivedString)
        dataReceivedFlag = False
    sleep_ms(loopIterationDuration_ms)