import sys

sys.path.append("")

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth
from imu import MPU6050
from machine import Pin, I2C, PWM
import math
import random
import struct

pwm = PWM(Pin(13))
pwm.freq(8)
#p0 = Pin(13, Pin.OUT)
#buz= machine.Pin('buz', machine.Pin.OUT)

# pwm.duty_u16(10000)
# pwm.duty_u16(30000)
# pwm.duty_u16(65535)



# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
_ENV_SENSE_GYRO_UUID = bluetooth.UUID(0x2B6E)

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
imu = MPU6050(i2c)

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

# Helper to decode the temperature characteristic encoding (sint16, hundredths of a degree).
def _decode_temperature(data):
    return struct.unpack("<h", data)[0] / 100

def _encode_temperature(temp_deg_c):
    return struct.pack("<h", int(temp_deg_c * 100))

async def get_gyro():
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
    
    return counter

async def find_temp_sensor():
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            # See if it matches our name and the environmental sensing service.
            if result.name() == "mpy-temp" and _ENV_SENSE_UUID in result.services():
                return result.device
    return None

async def main():
    device = await find_temp_sensor()
    if not device:
        print("Temperature sensor not found")
        return

    try:
        print("Connecting to", device)
        connection = await device.connect()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return

    async with connection:
        try:
            temp_service = await connection.service(_ENV_SENSE_UUID)
            
            temp_characteristic = await temp_service.characteristic(_ENV_SENSE_TEMP_UUID)
            gyro_characteristic = await temp_service.characteristic(_ENV_SENSE_GYRO_UUID)
            
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics")
            return

        while True:
            try:
                temp_data = await temp_characteristic.read()
                if temp_data is not None:
                    temp_deg_c = _decode_temperature(temp_data)
                    print("Temperature: {:.2f}".format(temp_deg_c))
                    if temp_deg_c == 0:
                        print("no")
                        #p0.value(1)
                        pwm.duty_u16(65535)
                        #time.sleep(0.01)
                    elif temp_deg_c == 1:
                        print("no")
                        #p0.value(1)
                        pwm.duty_u16(35000)
                        #time.sleep(0.01)
                    elif temp_deg_c == 2:
                        print("no")
                        #p0.value(1)
                        pwm.duty_u16(10000)
                        #time.sleep(0.01)
                    else:
                        print("yes")
                        
                        pwm.duty_u16(0)
                else:
                    print("Received None data from Bluetooth device.")
            except Exception as e:
                print("Error:", str(e))
            
            gyroint = await get_gyro()
            await gyro_characteristic.write(_encode_temperature(gyroint))
            
            await asyncio.sleep_ms(1000)

asyncio.run(main())