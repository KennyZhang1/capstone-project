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
led = machine.Pin('LED', machine.Pin.OUT)
led.on()
hall_effect = Pin(15,Pin.IN)
#p0 = Pin(13, Pin.OUT)
#buz= machine.Pin('buz', machine.Pin.OUT)

# pwm.duty_u16(10000)
# pwm.duty_u16(30000)
# pwm.duty_u16(65535)


# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)

_ENV_SENSE_ULTRA_UUID = bluetooth.UUID(0x2A6E)
_ENV_SENSE_GYRO_UUID = bluetooth.UUID(0x2B6E)
_ENV_SENSE_HALL_UUID = bluetooth.UUID(0x2C6E)

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
imu = MPU6050(i2c)

def calculate_tilt_angles(accel_data):
    x, y, z = accel_data['x'], accel_data['y'], accel_data['z']
 
    tilt_x = int(math.atan2(y, math.sqrt(x * x + z * z)) * 180 / math.pi)
    tilt_y = int(math.atan2(-x, math.sqrt(y * y + z * z)) * 180 / math.pi)
 
    return tilt_x, tilt_y

def package_data(ax, ay, az):
    return {
        'accel': {
            'x': ax,
            'y': ay,
            'z': az,
        }
    }

# Helper to decode the characteristic encodings (sint16, hundredths of a degree).
def _decode_int(data):
    return struct.unpack("<h", data)[0] / 100

def _encode_gyro_data(y_power, x_power, y_dir, x_dir):
    return struct.pack("<hhhh", y_power, x_power, y_dir, x_dir)

def _encode_hall_effect(val):
    return struct.pack("<h", int(val))

async def get_gyro():
    ax=round(imu.accel.x,2)
    ay=round(imu.accel.y,2)
    az=round(imu.accel.z,2)

    data_gyro = package_data(ax, ay, az)

    tilt_x, tilt_y = calculate_tilt_angles(data_gyro['accel'])
    
    y_power = 0
    x_power = 0
    y_dir = 0
    x_dir = 0
    
    abs_y_tilt = abs(tilt_y)
    abs_x_tilt = abs(tilt_x)
    
    y_power = abs_y_tilt
    x_power = abs_x_tilt
    
#     if abs_y_tilt < 25:
#         y_power = 0
#     elif abs_y_tilt < 45:
#         y_power = 1
#     elif abs_y_tilt < 65:
#         y_power = 2
#     else:
#         y_power = 3
# 
#     if abs_x_tilt < 15:
#         x_power = 0
#     elif abs_x_tilt < 40:
#         x_power = 1
#     elif abs_x_tilt < 70:
#         x_power = 2
#     else:
#         x_power = 3
#         
    if tilt_y >= 0:
        y_dir = 1
    else:
        y_dir = -1
    
    if tilt_x >= 0:
        x_dir = 1
    else:
        x_dir = -1
     
    
    return y_power, x_power, y_dir, x_dir

async def find_robot_pico():
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            # See if it matches our name and the environmental sensing service.
            if result.name() == "mpy-board" and _ENV_SENSE_UUID in result.services():
                return result.device
    return None

async def main():
    device = await find_robot_pico()
    if not device:
        print("Robot board not found")
        return
    try:
        print("Connecting to", device)
        connection = await device.connect()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return

    async with connection:
        try:
            conn_service = await connection.service(_ENV_SENSE_UUID)
            
            ultra_characteristic = await conn_service.characteristic(_ENV_SENSE_ULTRA_UUID)
            gyro_characteristic = await conn_service.characteristic(_ENV_SENSE_GYRO_UUID)
            hall_effect_characteristic = await conn_service.characteristic(_ENV_SENSE_HALL_UUID)
            
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics")
            return

        while True:
            try:
                ultra_data = await ultra_characteristic.read()
                if ultra_data is not None:
                    dist_ultra = _decode_int(ultra_data)
                    print("Ultrasonic Distance: {:.2f}".format(dist_ultra))
                    if dist_ultra == 0:
                        print("no")
                        pwm.duty_u16(65535)
                    elif dist_ultra == 1:
                        print("no")
                        pwm.duty_u16(35000)
                    elif dist_ultra == 2:
                        print("no")
                        pwm.duty_u16(10000)
                    else: 
                        print("yes")
                        
                        pwm.duty_u16(0)
                else:
                    print("Received None data from Bluetooth device.")
            except Exception as e:
                print("Error:", str(e))
            
            y_power, x_power, y_dir, x_dir = await get_gyro()
            await gyro_characteristic.write(_encode_gyro_data(y_power, x_power, y_dir, x_dir))
            
            hall_value = hall_effect.value()
            await hall_effect_characteristic.write(_encode_hall_effect(hall_value))
            
            await asyncio.sleep_ms(11)

asyncio.run(main()) 
