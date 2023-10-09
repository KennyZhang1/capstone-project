# Resource for code
# https://how2electronics.com/interfacing-mpu6050-with-raspberry-pi-pico-micropython/

#Shows Pi is on by turning on LED when plugged in
LED = machine.Pin("LED", machine.Pin.OUT)
LED.on()

from machine import Pin, I2C
import utime
import math
from imu import MPU6050
# from mpu6050 import init_mpu6050, get_mpu6050_data
 
def calculate_tilt_angles(accel_data):
    x, y, z = accel_data['x'], accel_data['y'], accel_data['z']
 
    tilt_x = math.atan2(y, math.sqrt(x * x + z * z)) * 180 / math.pi
    tilt_y = math.atan2(-x, math.sqrt(y * y + z * z)) * 180 / math.pi
    tilt_z = math.atan2(z, math.sqrt(x * x + y * y)) * 180 / math.pi
 
    return tilt_x, tilt_y, tilt_z
 
def complementary_filter(pitch, roll, gyro_data, dt, alpha=0.98):
    pitch += gyro_data['x'] * dt
    roll -= gyro_data['y'] * dt
 
    pitch = alpha * pitch + (1 - alpha) * math.atan2(gyro_data['y'], math.sqrt(gyro_data['x'] * gyro_data['x'] + gyro_data['z'] * gyro_data['z'])) * 180 / math.pi
    roll = alpha * roll + (1 - alpha) * math.atan2(-gyro_data['x'], math.sqrt(gyro_data['y'] * gyro_data['y'] + gyro_data['z'] * gyro_data['z'])) * 180 / math.pi
 
    return pitch, roll

def package_data(ax, ay, az, gx, gy, gz):
    return {
        'accel': {
            'x': ax,
            'y': ay,
            'z': az,
        },
        'gyro': {
            'x': gx,
            'y': gy,
            'z': gz,
        }
    }
 
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
imu = MPU6050(i2c)
 
pitch = 0
roll = 0
prev_time = utime.ticks_ms()
 
while True:
#     data = get_mpu6050_data(i2c)
    ax=round(imu.accel.x,2)
    ay=round(imu.accel.y,2)
    az=round(imu.accel.z,2)
    gx=round(imu.gyro.x)
    gy=round(imu.gyro.y)
    gz=round(imu.gyro.z)
    
    data = package_data(ax, ay, az, gx, gy, gz)
    curr_time = utime.ticks_ms()
    dt = (curr_time - prev_time) / 1000
 
    tilt_x, tilt_y, tilt_z = calculate_tilt_angles(data['accel'])
    pitch, roll = complementary_filter(pitch, roll, data['gyro'], dt)
 
    prev_time = curr_time
 
#     print("Temperature: {:.2f} °C".format(data['temp']))
#     print("Tilt angles: X: {:.2f}, Y: {:.2f}, Z: {:.2f} degrees".format(tilt_x, tilt_y, tilt_z))
#     print("Pitch: {:.2f}, Roll: {:.2f} degrees".format(pitch, roll))
    output=""
    if tilt_y < -30:
        output+="Go Forward Y: {:.2f},".format(tilt_y)
    elif tilt_y > 30:
        output+="Go Backward Y: {:.2f},".format(tilt_y)
    else:
        output+="Stay Y: {:.2f},".format(tilt_y)
        
    if tilt_x < -15:
        output+=" Turn Right X: {:.2f},".format(tilt_x)
    elif tilt_x > 15:
        output+=" Turn Left X: {:.2f},".format(tilt_x)
    else:
        output+=" Stay X: {:.2f},".format(tilt_x)
        
    print(output)
    
    print("\r")
#     print("Acceleration: X: {:.2f}, Y: {:.2f}, Z: {:.2f} g".format(data['accel']['x'], data['accel']['y'], data['accel']['z']))
#     print("Gyroscope: X: {:.2f}, Y: {:.2f}, Z: {:.2f} °/s".format(data['gyro']['x'], data['gyro']['y'], data['gyro']['z']))
    utime.sleep(1)
