# Example for Pycom device.
# Connections:
# xxPy | QMC5883
# -----|-------
# P9   |  SDA
# P10  |  SCL
#
from machine import I2C, Pin
from qmc5883l import QMC5883L
import time


i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=100000)
qmc5883 = QMC5883L(i2c)

while True:
    x, y, z, _ = qmc5883.read_scaled()
    print("X: ", x, "\tY: ", y, "\tZ: ", z)
    time.sleep(1)
