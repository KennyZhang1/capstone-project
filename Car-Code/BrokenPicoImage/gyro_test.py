#Shows Pi is on by turning on LED when plugged in
LED = machine.Pin("LED", machine.Pin.OUT)
LED.on()

IO = machine.Pin(3, machine.Pin.OUT)
IO.on()



from imu import MPU6050
from time import sleep
from machine import Pin, I2C

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
#i2c2 = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
imu = MPU6050(i2c)
#imu2 = MPU6050(i2c2)



while True:
    ax=round(imu.accel.x,2)
    ay=round(imu.accel.y,2)
    az=round(imu.accel.z,2)
    gx=round(imu.gyro.x)
    gy=round(imu.gyro.y)
    gz=round(imu.gyro.z)
    tem=round(imu.temperature,2)
    #print("ax",ax,"\t","ay",ay,"\t","az",az,"\t","gx",gx,"\t","gy",gy,"\t","gz",gz,"\t","Temperature",tem,"        ",end="\r")
    
    
#     ax2=round(imu2.accel.x,2)
#     ay2=round(imu2.accel.y,2)
#     az2=round(imu2.accel.z,2)
#     gx2=round(imu2.gyro.x)
#     gy2=round(imu2.gyro.y)
#     gz2=round(imu2.gyro.z)
#     tem2=round(imu2.temperature,2)
    #print("ax",ax,"\t","ay",ay,"\t","az",az,"\t","gx",gx,"\t","gy",gy,"\t","gz",gz,"\t","Temperature",tem,"        ","\n","ax2",ax2,"\t","ay2",ay2,"\t","az2",az2,"\t","gx2",gx2,"\t","gy2",gy2,"\t","gz2",gz2,"\t","Temperature2",tem2,"        ",end="\r")
    
    #print("ax", ax, )#"ax2", ax2, "\n", "ay", ay, "ay2", ay2, end="\r")
    #print("ay", ay, )
    print("ax", ax)
    sleep(0.2)

