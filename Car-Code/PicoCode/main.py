import uasyncio as asyncio
import aioble
import bluetooth
import struct
from machine import PWM, Pin
import utime

# Constants for ultrasonic sensor pins
TRIGGER_PIN = 15
ECHO_PIN = 14

# Constants for Bluetooth advertising
ENV_SENSE_UUID = bluetooth.UUID(0x181A)

ENV_SENSE_ULTRA_UUID = bluetooth.UUID(0x2A6E)
GYRO_RECEIVE_UUID = bluetooth.UUID(0x2B6E)
HALL_RECEIVE_UUID = bluetooth.UUID(0x2C6E)
ADV_APPEARANCE_GENERIC_BOARD = const(768)
ADV_INTERVAL_MS = 250_000

duty_cycle = 65535

ENA = PWM(Pin(0))        
IN1 = Pin(1, Pin.OUT)         
IN2 = Pin(2, Pin.OUT)
IN3 = Pin(3, Pin.OUT)
IN4 = Pin(4, Pin.OUT)
ENB = PWM(Pin(5))
ENA.freq(150)
ENB.freq(150)
#ENA.duty_u16(duty_cycle)
#ENB.duty_u16(duty_cycle)

# Create Pin objects for the ultrasonic sensor
trigger = Pin(TRIGGER_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)
led = machine.Pin('LED', machine.Pin.OUT)
led.on()

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
    
    if(distance < 15):
        return 0
    elif(distance < 25):
        return 1
    elif(distance < 35):
        return 2
    else:
        return 3

# Helper to encode the sensor characteristics (sint16, hundredths of a degree)
def encode_int(num):
    return struct.pack("<h", int(num * 100))

def decode_int(data):
    return struct.unpack("<h", data)[0] /100

def decode_hall_effect(data):
    return struct.unpack("<h", data)[0]


# Periodically update the ultrasonic characteristic
async def read_ultrasonic(ultra_characteristic):
    while True:
        try:
            # Measure distance using the ultrasonic sensor
            distance = measure_distance()
            
            print("US distance: ", distance)

            # Update the ultra characteristic with the distance value
            ultra_characteristic.write(encode_int(distance))
        except Exception as e:
            print("Error in sensor_task:", e)

        await asyncio.sleep_ms(1000)

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
        except Exception as e:
            print("Error in peripheral_task:", e)
            
async def recieve_gyro_data(gyro_receive_characteristic):
    # Inside your central device code when you want to read data:
    while True:
        connection, data = await gyro_receive_characteristic.written()
        receivedNumber = decode_int(data)
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
        await asyncio.sleep_ms(1000)
        
async def recieve_hall_data(hall_receive_characteristic, duty_cycle):
    # Inside your central device code when you want to read data:
    while True:
        connection, data = await hall_receive_characteristic.written()
        receivedNumber = decode_hall_effect(data)
        if receivedNumber == 0:
            duty_cycle=10000
            ENA.duty_u16(duty_cycle)
            ENB.duty_u16(duty_cycle)
        else:
            duty_cycle=65535
            ENA.duty_u16(duty_cycle)
            ENB.duty_u16(duty_cycle)
            
        print("Hall Number: ", receivedNumber)
        print("Motor Duty Cycle: ", duty_cycle)
        await asyncio.sleep_ms(1000)

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
        recieve_gyro_data(gyro_receive_characteristic),
        recieve_hall_data(hall_receive_characteristic, duty_cycle),
        advertise_board(),
    )

# Start the main event loop
asyncio.run(main())