import uasyncio as asyncio
import aioble
import bluetooth
import struct
from machine import PWM, Pin
import utime
import math
from L298N_motor import L298N

# Constants for pins
TRIGGER_PIN = 15
ECHO_PIN = 14

    #motor pins
BACK_LEFT_EN = 5
BACK_LEFT_IN1 = 3
BACK_LEFT_IN2 = 4

BACK_RIGHT_EN = 0
BACK_RIGHT_IN1 = 1
BACK_RIGHT_IN2 = 2

FRONT_LEFT_EN = 28
FRONT_LEFT_IN1 = 27
FRONT_LEFT_IN2 = 26

FRONT_RIGHT_EN = 20
FRONT_RIGHT_IN1 = 22
FRONT_RIGHT_IN2 = 21

# Constants for Bluetooth advertising
ENV_SENSE_UUID = bluetooth.UUID(0x181A)

ENV_SENSE_ULTRA_UUID = bluetooth.UUID(0x2A6E)
GYRO_RECEIVE_UUID = bluetooth.UUID(0x2B6E)
HALL_RECEIVE_UUID = bluetooth.UUID(0x2C6E)
ADV_APPEARANCE_GENERIC_BOARD = const(768)
ADV_INTERVAL_MS = 250_000

# timing constants
duty_cycle = 65535
delay_ms = 11


back_right = L298N(BACK_RIGHT_EN, BACK_RIGHT_IN1, BACK_RIGHT_IN2)
back_left = L298N(BACK_LEFT_EN, BACK_LEFT_IN1, BACK_LEFT_IN2)
front_right = L298N(FRONT_RIGHT_EN, FRONT_RIGHT_IN1, FRONT_RIGHT_IN2)
front_left = L298N(FRONT_LEFT_EN, FRONT_LEFT_IN1, FRONT_LEFT_IN2)

# Create Pin objects for the ultrasonic sensor
trigger = Pin(TRIGGER_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)
led = machine.Pin('LED', machine.Pin.OUT)
led.on()

# Global queues/vars for disconnect handling
gyro_queue = []
curr_gyro = 0
num_gcycles = 0
#hall_queue = []

# Function to perform ultrasonic distance measurement
def measure_distance():
    # Generate a trigger pulse
    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(5)
    trigger.low()

    # Initialize variables for measuring the duration of the echo pulse
    start_time = utime.ticks_us()
    end_time = start_time

    # Wait for the echo pulse to start
    while echo.value() == 0:
        if utime.ticks_diff(utime.ticks_us(), start_time) > 10000:  # Timeout after 10 milliseconds
            return 3  # Return None to indicate a timeout

    # Measure the duration of the echo pulse
    while echo.value() == 1:
        end_time = utime.ticks_us()

    # Calculate the time passed in microseconds
    time_passed = utime.ticks_diff(end_time, start_time)

    # Calculate distance in centimeters
    distance = (time_passed * 0.0343) / 2
    
    if(distance < 30):
        return 0
    elif(distance < 50):
        return 1
    elif(distance < 70):
        return 2
    else:
        return 3

# Helper to encode the sensor characteristics (sint16, hundredths of a degree)
def encode_int(num):
    return struct.pack("<h", int(num * 100))

def decode_gyro_data(data):
    return struct.unpack("<hhhh", data)

def decode_hall_effect(data):
    return struct.unpack("<h", data)[0]


# Periodically update the ultrasonic characteristic
async def read_ultrasonic(ultra_characteristic):
    while True:
        try:
            # Measure distance using the ultrasonic sensor
            distance = measure_distance()
            
            #print("US distance: ", distance)

            # Update the ultra characteristic with the distance value
            ultra_characteristic.write(encode_int(distance))
        except Exception as e:
            print("Error in sensor_task:", e)

        await asyncio.sleep_ms(delay_ms)

# Serially wait for connections and advertise
async def advertise_board():
    while True:
        try:
            async with await aioble.advertise(
                ADV_INTERVAL_MS,
                name="mpy-board",
                services=[ENV_SENSE_UUID],
                appearance=ADV_APPEARANCE_GENERIC_BOARD,
            ) as connection:
                print("Connection from", connection.device)
                await connection.disconnected(timeout_ms=None)
                print("Car Disconnected")
#                 await disconnect_handler()
                
        except Exception as e:
            print("Error in peripheral_task:", e)
            
def motor_scaling_y(power):
    dc = 0
    if power==0:
        dc = 0
    elif power==1:
        dc = 18000
    elif power==2:
        dc = 35000
    elif power==3:
        dc = 65535
    
    return dc

def motor_scaling_x_strafe(power):
    dc = 0
    if power==0:
        dc = 0
    elif power==1:
        dc = 20000
    elif power==2:
        dc = 35000
    elif power==3:
        dc = 65535
    
    return dc

def motor_scaling_x_spin(power):
    dc = 0
    if power==0:
        dc = 0
    elif power==1:
        dc = 20000
    elif power==2:
        dc = 35000
    elif power==3:
        dc = 65535
    
    return dc
    
# Function to read gyro number and spin motors
async def recieve_gyro_data(gyro_receive_characteristic, hall_receive_characteristic):
    global curr_gyro
    global num_gcycles
    
    motion=""
    
    while True:
        connection, data = await gyro_receive_characteristic.written()
        hall_connection, hall_data = await hall_receive_characteristic.written()
        orientation_lock = decode_hall_effect(hall_data)
        
        data_tuple = decode_gyro_data(data)
        y_power = data_tuple[0]
        x_power = data_tuple[1]
        y_dir = data_tuple[2]
        x_dir = data_tuple[3]
        
        print("YPerc: ", y_power/85, "XPerc: ", x_power/85,"YDir: ", y_dir, "XDir: ", x_dir)
        
        y = min(y_power/85, 1)
        x = min(x_power/85, 1)
        
        y_calc = y*y_dir
        x_calc = x*x_dir

        denominator = max(y + x, 1);
        
        frontLeftPower = (y_calc + x_calc) / denominator;
        backLeftPower = (y_calc - x_calc) / denominator;
        frontRightPower = (y_calc - x_calc) / denominator;
        backRightPower = (y_calc + x_calc) / denominator;
        
        back_right.setSpeedPercAndDir(backRightPower)
        back_left.setSpeedPercAndDir(backLeftPower)
        front_right.setSpeedPercAndDir(frontRightPower)
        front_left.setSpeedPercAndDir(frontLeftPower)


# 
# 
#         if y_power >= x_power:
#             motion = "Y"
#         else:
#             motion = "X"
#             
#   
#         if motion == "Y":
#             if y_dir > 0: # forward
#                 back_right.forward()
#                 back_left.forward()
#                 front_right.forward()
#                 front_left.forward()
#                 
#                 print("moving forward")
#                 
#             elif y_dir < 0: # backward
#                 back_right.backward()
#                 back_left.backward()
#                 front_right.backward()
#                 front_left.backward()
#                 
#                 print("moving backward")
#                 
#             current_duty_cycle = motor_scaling_y(y_power)
#             
#             back_right.setSpeed(current_duty_cycle)
#             back_left.setSpeed(current_duty_cycle)
#             front_right.setSpeed(current_duty_cycle)
#             front_left.setSpeed(current_duty_cycle)
#             
#         if motion == "X" and orientation_lock == 1:
#             if x_dir > 0: # right strafe
#                 front_left.forward()
#                 front_right.backward()
#                 back_left.backward()
#                 back_right.forward()
#                 
#                 print("strafe right")
#                 
#             elif x_dir < 0: # left strafe
#                 front_left.backward()
#                 front_right.forward()
#                 back_left.forward()
#                 back_right.backward()
#                 
#                 print("strafe left")
#             
#             current_duty_cycle = motor_scaling_x_spin(x_power)
#             back_right.setSpeed(current_duty_cycle)
#             back_left.setSpeed(current_duty_cycle)
#             front_right.setSpeed(current_duty_cycle)
#             front_left.setSpeed(current_duty_cycle)
#             
#         if motion == "X" and orientation_lock == 0:
#             if x_dir > 0: # right spinturn
#                 front_left.forward()
#                 front_right.backward()
#                 back_left.forward()
#                 back_right.backward()
#                 
#                 print("right spinturn")
#                 
#             elif x_dir < 0: # left spinturn
#                 front_left.backward()
#                 front_right.forward()
#                 back_left.backward()
#                 back_right.forward()
#                 
#                 print("left spinturn")
#             
#             current_duty_cycle = motor_scaling_x_spin(x_power)
#             back_right.setSpeed(current_duty_cycle)
#             back_left.setSpeed(current_duty_cycle)
#             front_right.setSpeed(current_duty_cycle)
#             front_left.setSpeed(current_duty_cycle)
#             

            
        
        print("O-lock: ", orientation_lock)
            
            
        await asyncio.sleep_ms(delay_ms)


# Run both tasks
async def main():
    # Register GATT server and create ultrasonic characteristic
    bluetooth_service = aioble.Service(ENV_SENSE_UUID)
    ultra_characteristic = aioble.Characteristic(
        bluetooth_service, ENV_SENSE_ULTRA_UUID, read=True, notify=True
    )
    
    # Create the gyro and hall effect recieve characteristics
    gyro_receive_characteristic = aioble.Characteristic(
        bluetooth_service, GYRO_RECEIVE_UUID, write=True, read=True, notify=True, capture=True
    )
    
    hall_receive_characteristic = aioble.Characteristic(
        bluetooth_service, HALL_RECEIVE_UUID, write=True, read=True, notify=True, capture=True
    )

    aioble.register_services(bluetooth_service)

    # Start the sensor send/recieve tasks
    await asyncio.gather(
        read_ultrasonic(ultra_characteristic),
        recieve_gyro_data(gyro_receive_characteristic, hall_receive_characteristic),
        advertise_board()
    )
    

# Start the main event loop
asyncio.run(main())











