#
# initial code by Sebastian Folz, M.Sc. at
# http://nobytes.blogspot.com/2018/03/qmc5883-magnetic-field-sensor.html
# which, I assume, was itself ported from C-Code
# See also https://github.com/RigacciOrg/py-qmc5883l
#
# Changes and Additions:
# - port to micropython's I2C methods
# - add method read_scaled() for scaled values
# - reading register values into a static buffer
# - parsed register values in one single struct call
# - fixed a bug in the method set_rate()
# - added value checks for the set_xxx methods()
# - changed method names according to PEP8
# - apply PyLint and fixed bugs & warnings reported by it
#

import time
import struct
from mag_base import mag_base

class QMC5883L(mag_base):
    # probe the existence of const()
    try:
        _canary = const(0xfeed)
    except:
        const = lambda x: x

    # Default I2C address
    ADDR = const(0x0D)

    # QMC5883 Register numbers
    X_LSB = const(0)
    X_MSB = const(1)
    Y_LSB = const(2)
    Y_MSB = const(3)
    Z_LSB = const(4)
    Z_MSB = const(5)
    STATUS = const(6)
    T_LSB = const(7)
    T_MSB = const(8)
    CONFIG = const(9)
    CONFIG2 = const(10)
    RESET = const(11)
    STATUS2 = const(12)
    CHIP_ID = const(13)

    # Bit values for the STATUS register
    STATUS_DRDY = const(1)
    STATUS_OVL = const(2)
    STATUS_DOR = const(4)

    # Oversampling values for the CONFIG register
    CONFIG_OS512 = const(0b00000000)
    CONFIG_OS256 = const(0b01000000)
    CONFIG_OS128 = const(0b10000000)
    CONFIG_OS64 = const(0b11000000)

    # Range values for the CONFIG register
    CONFIG_2GAUSS = const(0b00000000)
    CONFIG_8GAUSS = const(0b00010000)

    # Rate values for the CONFIG register
    CONFIG_10HZ = const(0b00000000)
    CONFIG_50HZ = const(0b00000100)
    CONFIG_100HZ = const(0b00001000)
    CONFIG_200HZ = const(0b00001100)

    # Mode values for the CONFIG register
    CONFIG_STANDBY = const(0b00000000)
    CONFIG_CONT = const(0b00000001)

    # Mode values for the CONFIG2 register
    CONFIG2_INT_DISABLE = const(0b00000001)
    CONFIG2_ROL_PTR = const(0b01000000)
    CONFIG2_SOFT_RST = const(0b10000000)

    def __init__(self, i2c, offset=50.0):
        super().__init__(i2c)

        self.temp_offset = offset
        self.oversampling = QMC5883L.CONFIG_OS64
        self.range = QMC5883L.CONFIG_2GAUSS
        self.rate = QMC5883L.CONFIG_100HZ
        self.mode = QMC5883L.CONFIG_CONT
        self.register = bytearray(9)
        self.command = bytearray(1)
        self.reset()

    def reset(self):
        self.command[0] = 1
        self.i2c.writeto_mem(QMC5883L.ADDR, QMC5883L.RESET, self.command)
        time.sleep(0.1)
        self.reconfig()

    def reconfig(self):
        self.command[0] = (self.oversampling | self.range |
                           self.rate | self.mode)
        self.i2c.writeto_mem(QMC5883L.ADDR, QMC5883L.CONFIG,
                             self.command)
        time.sleep(0.01)
        self.command[0] = QMC5883L.CONFIG2_INT_DISABLE
        self.i2c.writeto_mem(QMC5883L.ADDR, QMC5883L.CONFIG2,
                             self.command)
        time.sleep(0.01)

    def set_oversampling(self, sampling):
        if (sampling << 6) in (QMC5883L.CONFIG_OS512, QMC5883L.CONFIG_OS256,
                               QMC5883L.CONFIG_OS128, QMC5883L.CONFIG_OS64):
            self.oversampling = sampling << 6
            self.reconfig()
        else:
            raise ValueError("Invalid parameter")

    def set_range(self, rng):
        if (rng << 4) in (QMC5883L.CONFIG_2GAUSS, QMC5883L.CONFIG_8GAUSS):
            self.range = rng << 4
            self.reconfig()
        else:
            raise ValueError("Invalid parameter")

    def set_sampling_rate(self, rate):
        if (rate << 2) in (QMC5883L.CONFIG_10HZ, QMC5883L.CONFIG_50HZ,
                           QMC5883L.CONFIG_100HZ, QMC5883L.CONFIG_200HZ):
            self.rate = rate << 2
            self.reconfig()
        else:
            raise ValueError("Invalid parameter")

    def ready(self):
        status = self.i2c.readfrom_mem(QMC5883L.ADDR, QMC5883L.STATUS, 1)[0]
        # prevent hanging up here.
        # Happens when reading less bytes then then all 3 axis and will
        # end up in a loop. So, return any data but avoid the loop.
        if status == QMC5883L.STATUS_DOR:
            print("Incomplete read")
            return QMC5883L.STATUS_DRDY

        return status & QMC5883L.STATUS_DRDY

    def read_raw(self):
        try:
            while not self.ready():
                time.sleep(0.005)
            self.i2c.readfrom_mem_into(QMC5883L.ADDR, QMC5883L.X_LSB,
                                       self.register)
        except OSError as error:
            print("OSError", error)
            pass  # just silently re-use the old values
        # Convert the axis values to signed Short before returning
        x, y, z, _, temp = struct.unpack('<hhhBh', self.register)

        return (x, y, z, temp)

    def read_scaled(self):
        x, y, z, temp = self.read_raw()
        scale = 12000 if self.range == QMC5883L.CONFIG_2GAUSS else 3000

        return (x / scale, y / scale, z / scale,
                (temp / 100 + self.temp_offset))


from machine import I2C, Pin
import time
import struct
import math

QMC5883L_ADDR = 0x0D
CONFIG_REG_A = 0x09
DATA_REG = 0x00

LSB_TO_UT = 0.732  # Conversion factor for QMC5883L, adjust as needed

i2c = I2C(0, scl=Pin(13), sda=Pin(12), freq=100000)

devices = i2c.scan()

device_count = len(devices)

if device_count == 0:
    print('No i2c device found.')
else:
    print(device_count, 'devices found.')

for device in devices:
    print('Decimal address:', device, ", Hex address: ", hex(device))


QMC5883 = QMC5883L(i2c)
QMC5883.reconfig()


min = 1000
max = 0

while True:
    (x, y, z, t) = QMC5883.read_raw()
    
    print("Raw Data: X=%d, Y=%d, Z=%d" % (x, y, z))

    # Calculate angle of Z-axis in degrees
    angle_z = math.atan2(y, x)
    angle_z_degrees = math.degrees(angle_z)
    
    if angle_z > max:
        max = angle_z
    if angle_z < min:
        min = angle_z

    print("Angle of Z-axis: %.2f degrees" % angle_z_degrees)
    print(x, y, z)
    

    
    

    time.sleep(0.1)

