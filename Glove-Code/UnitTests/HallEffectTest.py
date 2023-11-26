import time
from machine import Pin

p25 = Pin('LED',Pin.OUT)

test_point = Pin(15,Pin.IN)



while True:
#     on_point.on()
#     time.sleep_ms(1000)
#     on_point.off()
#     time.sleep_ms(1000)
    print(test_point.value())
    time.sleep_ms(1000)


# from machine import Pin, ADC
# import time
# 
# 
# # Create an ADC object linked to pin 26
# adc = ADC(Pin(26, mode=Pin.IN))
# 
# while True:
# 
#     # Read ADC and convert to voltage
#     val = adc.read_u16()
#     print(val)
# #     val = val * (3.3 / 65535)
# #     print(round(val, 2), "V") # Keep only 2 digits
# 
#     # Wait a bit before taking another reading
#     time.sleep_ms(100)