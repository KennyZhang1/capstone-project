# Resource for code
# https://how2electronics.com/interfacing-mpu6050-with-raspberry-pi-pico-micropython/
# https://thepihut.com/blogs/raspberry-pi-tutorials/wireless-communication-between-two-raspberry-pi-pico-w-boards

#Shows Pi is on by turning on LED when plugged in
LED = machine.Pin("LED", machine.Pin.OUT)
LED.on()

# Imports
import network
import time
import socket
from machine import Pin, I2C
import utime
import math
from imu import MPU6050

# Helper functions
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

# I2C connection
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
imu = MPU6050(i2c)
 
pitch = 0
roll = 0
prev_time = utime.ticks_ms()

# WIFI credentials and server IP
ssid = ""
password = ""
server_ip = ""

# use wlan to connect
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
while not wlan.isconnected() and wlan.status() >= 0:
    print("Waiting to connect:")
    time.sleep(1)
 
# Should be connected and have an IP address
wlan.status() # 3 == success
wlan.ifconfig()
print(wlan.ifconfig())

# Initiate socket to server
ai = socket.getaddrinfo(server_ip, 80) 
addr = ai[0][-1]
s = socket.socket()
s.connect(addr)

# Main loop
while True:
    # Format data from 6050
    # data = get_mpu6050_data(i2c)
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
 
    # Form output string
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
    
    # Send gyro output to server (robot)
    output_enc = output.encode("utf-8") 
    s.send(output_enc)
    
    # Get ultrasonic output from server (robot)
    response = s.recv(1024)
    ultra = response.decode("utf-8")
    print(ultra)
         
    utime.sleep(0.2)