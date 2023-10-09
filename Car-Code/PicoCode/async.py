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

ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
CUSTOM_RECEIVE_UUID = bluetooth.UUID(0x2B6E)
ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)
ADV_INTERVAL_MS = 250_000

ENA = PWM(Pin(0))        
IN1 = Pin(1, Pin.OUT)         
IN2 = Pin(2, Pin.OUT)
IN3 = Pin(3, Pin.OUT)
IN4 = Pin(4, Pin.OUT)
ENB = PWM(Pin(5))
ENA.freq(150)
ENB.freq(150)
ENA.duty_u16(65535)
ENB.duty_u16(65535)

# Create Pin objects for the ultrasonic sensor
trigger = Pin(TRIGGER_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

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
        if utime.ticks_diff(utime.ticks_us(), start_time) > 100000:  # Timeout after 10 milliseconds
            return 10000  # Return None to indicate a timeout

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

# Helper to encode the temperature characteristic (sint16, hundredths of a degree)
def encode_temperature(temp_deg_c):
    return struct.pack("<h", int(temp_deg_c * 100))

def decode_temperature(data):
    return struct.unpack("<h", data)[0] /100


# Periodically update the temperature characteristic
async def sensor_task(temp_characteristic):
    while True:
        try:
            # Measure distance using the ultrasonic sensor
            distance = measure_distance()

            # Update the temperature characteristic with the distance value
            temp_characteristic.write(encode_temperature(distance))
        except Exception as e:
            print("Error in sensor_task:", e)

        await asyncio.sleep_ms(1000)

# Serially wait for connections and advertise
async def peripheral_task():
    while True:
        try:
            async with await aioble.advertise(
                ADV_INTERVAL_MS,
                name="mpy-temp",
                services=[ENV_SENSE_UUID],
                appearance=ADV_APPEARANCE_GENERIC_THERMOMETER,
            ) as connection:
                print("Connection from", connection.device)
                await connection.disconnected(timeout_ms=None)
        except Exception as e:
            print("Error in peripheral_task:", e)
            
async def recieve_data(custom_receive_characteristic):
    # Inside your central device code when you want to read data:
    while True:
        connection, data = await custom_receive_characteristic.written()
        receivedNumber = decode_temperature(data)
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

# Run both tasks
async def main():
    # Register GATT server and create temperature characteristic
    temp_service = aioble.Service(ENV_SENSE_UUID)
    temp_characteristic = aioble.Characteristic(
        temp_service, ENV_SENSE_TEMP_UUID, read=True, notify=True
    )
    
    # Create the custom data receiving characteristic
    custom_receive_characteristic = aioble.Characteristic(
        temp_service, CUSTOM_RECEIVE_UUID, write=True, read=True, notify=True, capture=True
    )

    aioble.register_services(temp_service)

    # Start the sensor and peripheral tasks
    await asyncio.gather(
        sensor_task(temp_characteristic),
        recieve_data(custom_receive_characteristic),
        peripheral_task(),
    )

# Start the main event loop
asyncio.run(main())
