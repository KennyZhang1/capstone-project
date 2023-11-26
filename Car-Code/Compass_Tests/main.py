# Example for Pycom device.
# Connections:
# xxPy | QMC5883
# -----|-------
# P9   |  SDA
# P10  |  SCL
#
from machine import I2C
from qmc5883l import QMC5883L


i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=100000)
qmc5883 = QMC5883L(i2c)

x, y, z, _ = qmc5883.read_scaled()