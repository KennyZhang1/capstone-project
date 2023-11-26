import time
from machine import Pin

print("Hello World")
p25 = Pin('LED',Pin.OUT)

while True:
  p25.on()
  time.sleep_ms(250)
  p25.off()
  time.sleep_ms(250)