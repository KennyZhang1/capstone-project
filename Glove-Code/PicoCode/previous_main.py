import machine
import time
import ustruct, bluetooth
from utime import sleep_ms
import utime
from micropython import const

from imu import MPU6050
import utime
import math
from machine import Pin, I2C, PWM

pwm = PWM(Pin(15))
pwm.freq(8)

def calculate_tilt_angles(accel_data):
    x, y, z = accel_data['x'], accel_data['y'], accel_data['z']
 
    tilt_x = math.atan2(y, math.sqrt(x * x + z * z)) * 180 / math.pi
    tilt_y = math.atan2(-x, math.sqrt(y * y + z * z)) * 180 / math.pi
    tilt_z = math.atan2(z, math.sqrt(x * x + y * y)) * 180 / math.pi
 
    return tilt_x, tilt_y, tilt_z

def package_data(ax, ay, az):
    return {
        'accel': {
            'x': ax,
            'y': ay,
            'z': az,
        }
    }


led = machine.Pin('LED', machine.Pin.OUT)
led.on()
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
imu = MPU6050(i2c)


# trigger = Pin(15, Pin.OUT)
# echo = Pin(14, Pin.IN)

# def ultra():
#     trigger.low()
#     utime.sleep_us(2)
#     trigger.high()
#     utime.sleep_us(5)
#     trigger.low()
# 
#     while echo.value() == 0:
#        signaloff = utime.ticks_us()
#        
#     while echo.value() == 1:
#        signalon = utime.ticks_us()
#        
#     timepassed = signalon - signaloff
#     #distance = (timepassed * 0.0343) / 2
#     return timepassed

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

advertisingInterval_us = int(1e6) # 1 second interval - just set as larger than the loop iteration duration, see below
loopIterationDuration_ms = 1000
serverAddress = bytes(b'(\xcd\xc1\x0bT\xa7')

scanDuration_ms = 100000  # Specify how long the scanning should take
interval_us = 15000
window_us = 15000  # The same window as interval, means continuous scan
active = False  # Do not care for a reply for a scan from the transmitter

receivedString = 0
dataReceivedFlag = False
ble.gap_scan(scanDuration_ms, interval_us, window_us, active)


while True:
        ax=round(imu.accel.x,2)
        ay=round(imu.accel.y,2)
        az=round(imu.accel.z,2)
        gx=round(imu.gyro.x)
        gy=round(imu.gyro.y)
        gz=round(imu.gyro.z)
        tem=round(imu.temperature,2)
        #print("ax",ax,"\t","ay",ay,"\t","az",az,"\t","gx",gx,"\t","gy",gy,"\t","gz",gz,"\t","Temperature",tem,"        ",end="\r")

        data_gyro1 = package_data(ax, ay, az)
 
        tilt_x1, tilt_y1, tilt_z1 = calculate_tilt_angles(data_gyro1['accel'])
        if tilt_y1 > 40:
            counter = 4
        elif tilt_y1 < -40:
            counter = 3
        elif tilt_x1 < -30:
            counter = 2
        elif tilt_x1 > 30:
            counter = 1
        else:
            counter = 0
        
        #return counter
        #if tilt_y1 < -15:
        #    output1+=" Turn Right Y: {:.2f},".format(tilt_y1)
        #elif tilt_y1 > 15:
        #    output1+=" Turn Left Y: {:.2f},".format(tilt_y1)
        #else:
        #    output1+=" Stay Y: {:.2f},".format(tilt_y1)
            
            
        
        advertisedData = ustruct.pack('<i',counter)
        #advertisedData = ustruct.pack('<i',counter)
        ble.gap_advertise(advertisingInterval_us,adv_data=advertisedData, connectable=False)
        #print("Received string" + receivedString)
        print(counter)
        sleep_ms(1000)
#         if dataReceivedFlag:
#             print(receivedString)
#             dataReceivedFlag = False
#         sleep_ms(1000)

    






