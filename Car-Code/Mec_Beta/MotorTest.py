import uasyncio as asyncio
import aioble
import bluetooth
import struct
from machine import PWM, Pin
import utime
import math

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

# timing constants
duty_cycle = 65535
delay_ms = 11

# motor pin inits
ENA = PWM(Pin(0))
IN1 = Pin(1, Pin.OUT)         
IN2 = Pin(2, Pin.OUT)
IN3 = Pin(3, Pin.OUT)
IN4 = Pin(4, Pin.OUT)
ENB = PWM(Pin(5))
ENC = PWM(Pin(28))
IN5 = Pin(27, Pin.OUT)         
IN6 = Pin(26, Pin.OUT)
IN7 = Pin(22, Pin.OUT)
IN8 = Pin(21, Pin.OUT)
END = PWM(Pin(20))

ENA.freq(150)
ENB.freq(150)
ENC.freq(150)
END.freq(150)
#ENA.duty_u16(duty_cycle)
#ENB.duty_u16(duty_cycle)

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
                await disconnect_handler()
                
        except Exception as e:
            print("Error in peripheral_task:", e)
            
def motor_scaling(input_perc):
    output_perc = 0
    if input_perc < 15:
        output_perc = 0
        print("Output Perc: ", output_perc)
    elif input_perc < 30:
        output_perc = (0.5*input_perc)+22.5
    elif input_perc < 65:
        input_perc = input_perc-30
        input_squared = input_perc**2
        input_scaled = input_squared * 0.015
        input_shifted = input_scaled + 37.5
        output_perc = input_shifted
    else:
        output_perc = input_perc-10
        
    print("Output Perc: ", output_perc)
    
    return output_perc
    

# Function to read gyro number and spin motors
async def recieve_gyro_data(gyro_receive_characteristic):
    global curr_gyro
    global num_gcycles
    
    while True:
        connection, data = await gyro_receive_characteristic.written()
        receivedNumber = decode_int(data)
        print("Gyro number:", receivedNumber)
        

            
        
        duty_cycle_damper = motor_scaling(abs(receivedNumber)) / 100
        max_duty_cycle = 65535
        
        current_duty_cycle = int(max_duty_cycle * duty_cycle_damper) 
        

        
        if receivedNumber > 0: # forward
            IN1.high()
            IN2.low()
            IN3.high()
            IN4.low()
            IN5.low()
            IN6.high()
            IN7.low()
            IN8.high()
            print("moving forward")
        elif receivedNumber < 0: # backward
            IN1.low()
            IN2.high()
            IN3.low()
            IN4.high()
            IN5.high()
            IN6.low()
            IN7.high()
            IN8.low()
        if duty_cycle_damper < 0.3:
            IN1.low()
            IN2.low()
            IN3.low()
            IN4.low()
            IN5.low()
            IN6.low()
            IN7.low()
            IN8.low()
            current_duty_cycle=0
            
        ENA.duty_u16(current_duty_cycle)
        ENB.duty_u16(current_duty_cycle)
        ENC.duty_u16(current_duty_cycle)
        END.duty_u16(current_duty_cycle)
        

        
        print(current_duty_cycle)
            
#         if receivedNumber == 0: # Stop
#             IN1.low()
#             IN2.low()
#             IN3.low()
#             IN4.low()
#         elif receivedNumber == 4:# Forward
#             IN1.low()
#             IN2.high()
#             IN3.high()
#             IN4.low()
#         elif receivedNumber == 3: # Backward
#             IN1.high()
#             IN2.low()
#             IN3.low()
#             IN4.high()
#         elif receivedNumber == 2: # Right
#             IN1.low()
#             IN2.high()
#             IN3.low()
#             IN4.low()
#         elif receivedNumber == 1: # Left
#             IN1.low()
#             IN2.low()
#             IN3.high()
#             IN4.low()
            
        if receivedNumber == curr_gyro:
            num_gcycles += 1
        else:
            if curr_gyro != 0:
                if (len(gyro_queue) > 0 and curr_gyro == gyro_queue[len(gyro_queue)-1][0]):
                    prev_tup = gyro_queue.pop()
                    gyro_queue.append((curr_gyro, prev_tup[1] + num_gcycles))
                else:
                    gyro_queue.append((curr_gyro, num_gcycles))
            curr_gyro = receivedNumber
            num_gcycles = 1
            
        await asyncio.sleep_ms(delay_ms)

# function to read hall number and trigger precision mode
async def recieve_hall_data(hall_receive_characteristic, duty_cycle):
    while True:
        connection, data = await hall_receive_characteristic.written()
        receivedNumber = decode_hall_effect(data)
        # precision mode
        if receivedNumber == 0:
            duty_cycle=25000
#             ENA.duty_u16(duty_cycle)
#             ENB.duty_u16(duty_cycle-3500)
        # standard mode
        else:
            duty_cycle=65535
#             ENA.duty_u16(duty_cycle)
#             ENB.duty_u16(duty_cycle-3500)
            
#         print("Hall Number: ", receivedNumber)
        #print("Motor Duty Cycle: ", duty_cycle)
        #hall_queue.append(receivedNumber)
        await asyncio.sleep_ms(delay_ms)

# handler function for disconnect
async def disconnect_handler():
    print("Returning car to initial position")
    duty_cycle=65535
    g = len(gyro_queue)
    '''
    h = len(hall_queue)
    # one extra gyro command. copy the most recent hall number to the empty spot
    if (g > h):
        print("interpolating hall number")
        hall_queue.append(hall_queue[h-1])
    # one extra hall number. discard it since it doesnt match a gyro command
    elif (h > g):
        print("discarding extra hall number")
        unused = hall_queue.pop()
    # queues match
    else:
        print("queue sizes match")
    # at this point, queues match
    '''
    for i in range(g-1, -1, -1):
        g_num = gyro_queue[i][0]
        cycles = gyro_queue[i][1]
        print("Found gyro number: " + str(g_num) + " for " + str(cycles) + " cycles")
        #h_num = hall_queue[i]
        for j in range(0, cycles):
            '''
            # set duty cycle depending on hall num
            if h_num == 0:
                duty_cycle=25000
                ENA.duty_u16(duty_cycle)
                ENB.duty_u16(duty_cycle-3500)
            else:
                duty_cycle=65535
                ENA.duty_u16(duty_cycle)
                ENB.duty_u16(duty_cycle-3500)
            '''
            
            # do the reverse of the gyro num
            # Case 4: go backwards
            if g_num == 4:
                IN1.high()
                IN2.low()
                IN3.low()
                IN4.high()
            # Case 3: go forwards
            elif g_num == 3:
                IN1.low()
                IN2.high()
                IN3.high()
                IN4.low()
            # Case 2: turn right back
            elif g_num == 2:
                IN1.high()
                IN2.low()
                IN3.low()
                IN4.low()
            # Case 1: turn left back
            elif g_num == 1:
                IN1.low()
                IN2.low()
                IN3.low()
                IN4.high()
                
            utime.sleep_ms(delay_ms*17)
            
    # stop the car once complete and reset queues
    IN1.low()
    IN2.low()
    IN3.low()
    IN4.low()
    IN5.low()
    IN6.low()
    IN7.low()
    IN8.low()
    print("Queue length: ", g)
    gyro_queue.clear()
    #hall_queue.clear()

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
        advertise_board()
    )
    

# Start the main event loop
asyncio.run(main())





