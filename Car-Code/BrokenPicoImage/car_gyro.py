#Shows Pi is on by turning on LED when plugged in
LED = machine.Pin("LED", machine.Pin.OUT)
LED.on()

IO = machine.Pin(3, machine.Pin.OUT)

IO.on()

from imu import MPU6050
import utime
import math
from machine import Pin, I2C
# Define a variable to keep track of time
prev_time = utime.ticks_us()
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
#i2c2 = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
imu = MPU6050(i2c)
#imu2 = MPU6050(i2c2)
def calculate_yaw(gyro_data, dt):
    gx, gy, gz = gyro_data['x'], gyro_data['y'], gyro_data['z']
    
    # Integrate gyro data to get yaw angle
    yaw = gz * dt  # This is a basic approximation, actual integration may be more complex
    
    return yaw

# Define initial values
yaw = 0
gyro_weight = 0.98  # Weight for gyro data
accel_weight = 1 - gyro_weight  # Weight for accelerometer data

# Define a variable to keep track of time
prev_time = utime.ticks_us()

while True:
    # Measure time since last iteration
    current_time = utime.ticks_us()
    dt = utime.ticks_diff(current_time, prev_time) / 1e6  # Convert microseconds to seconds
    prev_time = current_time

    ax = imu.accel.x
    ay = imu.accel.y
    az = imu.accel.z
    gx = imu.gyro.x
    gy = imu.gyro.y
    gz = imu.gyro.z

    # Integrate gyroscope data to get short-term yaw change
    yaw_change = gz * dt

    # Update yaw with a weighted combination of gyro and accel data
    yaw += gyro_weight * yaw_change

    # Use accelerometer data to correct for long-term drift
    accel_yaw = math.atan2(ay, ax) * 180 / math.pi
    accel_yaw = accel_yaw if accel_yaw >= 0 else 360 + accel_yaw  # Convert to [0, 360] range
    yaw = accel_weight * accel_yaw + gyro_weight * yaw

    output1 = ""
    if yaw < -30:
        output1 += "Car moving left: {:.2f},".format(yaw)
    elif yaw > 30:
        output1 += "Car moving right: {:.2f},".format(yaw)
    else:
        output1 += "Car going straight: {:.2f},".format(yaw)

    print(output1, "|||| \t ||||", end="\r")

    utime.sleep(1)