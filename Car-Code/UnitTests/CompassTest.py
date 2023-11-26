from machine import I2C, Pin
import time
import math
 
# HMC5883L address and register addresses
HMC5883L_ADDR = 0xD
CONFIG_REG_A = 0x00
CONFIG_REG_B = 0x01
MODE_REG = 0x02
DATA_REG_A = 0x03
DATA_REG_B = 0x04
 
# Conversion factor from raw value to uT
# With default gain 1 Ga = 1090 LSb
# And 1 Ga = 100 uT, therefore 1 LSb = 100 uT / 1090 LSb
LSB_TO_UT = 100.0 / 1090.0
 
# Initialize I2C
i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=100000)

devices = i2c.scan() # this returns a list of devices

device_count = len(devices)

if device_count == 0:
    print('No i2c device found.')
else:
    print(device_count, 'devices found.')

for device in devices:
    print('Decimal address:', device, ", Hex address: ", hex(device))
 
# Check if HMC5883L is connected
# if HMC5883L_ADDR not in i2c.scan():
#     raise ValueError('HMC5883L not found')
 
# Write configuration to HMC5883L
# Continuous measurement mode, 15Hz data output rate
i2c.writeto(HMC5883L_ADDR, bytes([0x3C, CONFIG_REG_A]))
i2c.writeto(HMC5883L_ADDR, bytes([0x3C, CONFIG_REG_A, 0x70]))

i2c.writeto(HMC5883L_ADDR, bytes([0x3C, CONFIG_REG_A]))
print("CONFIG REG A: ", hex(i2c.readfrom(HMC5883L_ADDR, 1)[0]))

# i2c.writeto(HMC5883L_ADDR, bytes([0x3C, CONFIG_REG_B]))
# i2c.writeto(HMC5883L_ADDR, bytes([0x3C, CONFIG_REG_B, 0x20]))
# 
# i2c.writeto(HMC5883L_ADDR, bytes([0x3C, MODE_REG]))
# i2c.writeto(HMC5883L_ADDR, bytes([0x3C, MODE_REG, 0x00]))


i2c.writeto(HMC5883L_ADDR, bytes([0x3C, CONFIG_REG_B]))
i2c.writeto(HMC5883L_ADDR, bytes([0x3C, CONFIG_REG_B, 0x20]))

i2c.writeto(HMC5883L_ADDR, bytes([0x3C, CONFIG_REG_B]))
print("CONFIG REG B: ", hex(i2c.readfrom(HMC5883L_ADDR, 1)[0]))

# i2c.writeto(HMC5883L_ADDR, bytes([0x3C, MODE_REG]))
# print("MODE REG: ", hex(i2c.readfrom(HMC5883L_ADDR, 1)[0]))

i2c.writeto(HMC5883L_ADDR, bytes([0x3C, MODE_REG]))
i2c.writeto(HMC5883L_ADDR, bytes([0x3C, MODE_REG, 0x0]))

i2c.writeto(HMC5883L_ADDR, bytes([0x3C, MODE_REG]))
print("MODE_REG: ", hex(i2c.readfrom(HMC5883L_ADDR, 1)[0]))

# i2c.writeto_mem(HMC5883L_ADDR, CONFIG_REG_A, bytes([0x70]))
# i2c.writeto_mem(HMC5883L_ADDR, CONFIG_REG_B, bytes([0x20]))
# i2c.writeto_mem(HMC5883L_ADDR, MODE_REG, bytes([0x00]))
 
while True:
    i2c.writeto(HMC5883L_ADDR, bytes([0x3C, DATA_REG_A]))
    data = i2c.readfrom(HMC5883L_ADDR, 6)
    print(data)
#     data_A = i2c.readfrom_mem(HMC5883L_ADDR, DATA_REG_A, 6)
#     print("DATA A: ", data_A)
#     
#     data_B = i2c.readfrom_mem(HMC5883L_ADDR, DATA_REG_B, 6)
#     print("DATA B: ", data_B)
#     
#     data_C = i2c.readfrom_mem(HMC5883L_ADDR, CONFIG_REG_A, 6)
#     print("readback: ", data_C)
#     
#     x = ((data[0] << 8) | data[1])
#     z = ((data[2] << 8) | data[3])
#     y = ((data[4] << 8) | data[5])
#     
#     if x > 32767:
#         x -= 65536
#     if y > 32767:
#         y -= 65536
#     if z > 32767:
#         z -= 65536
#  
#     # Convert to uT
#     x *= LSB_TO_UT
#     y *= LSB_TO_UT
#     z *= LSB_TO_UT
#  
#     # Calculate heading in degrees
#     heading = math.atan2(y, x)
#     
#     # Convert radian to degree
#     heading = math.degrees(heading)
#     
#     # Due to declination, the heading may need to be corrected
#     # Declination is the error between magnetic north and true north, depending on your geographical location. 
#     # Here, let's assume we have a declination of 0 degrees. If you know the declination in your area, put it instead.
#     declination_angle = 0.0
#     heading += declination_angle
#     
#     # Correct negative values
#     if heading < 0:
#         heading += 360
#     
#     print("Magnetic field in X: %.2f uT, Y: %.2f uT, Z: %.2f uT, Heading: %.2f°" % (x, y, z, heading))
    time.sleep(0.1)