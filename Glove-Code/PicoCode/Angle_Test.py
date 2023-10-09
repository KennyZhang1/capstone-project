#Shows Pi is on by turning on LED when plugged in
LED = machine.Pin("LED", machine.Pin.OUT)
LED.on()

IO = machine.Pin(3, machine.Pin.OUT)

IO.on()



from imu import MPU6050
import utime
import math
from machine import Pin, I2C

def calculate_tilt_angles(accel_data):
    x, y, z = accel_data['x'], accel_data['y'], accel_data['z']
 
    tilt_x = math.atan2(y, math.sqrt(x * x + z * z)) * 180 / math.pi
    tilt_y = math.atan2(-x, math.sqrt(y * y + z * z)) * 180 / math.pi
    tilt_z = math.atan2(z, math.sqrt(x * x + y * y)) * 180 / math.pi
 
    return tilt_x, tilt_y, tilt_z

def package_data(ax, ay, az):
    return {
        'accel': {
            'x': ax,
            'y': ay,
            'z': az,
        }
    }

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

    data_gyro1 = package_data(ax, ay, az)
 
    tilt_x1, tilt_y1, tilt_z1 = calculate_tilt_angles(data_gyro1['accel'])

#     ax2=round(imu2.accel.x,2)
#     ay2=round(imu2.accel.y,2)
#     az2=round(imu2.accel.z,2)
#     gx2=round(imu2.gyro.x)
#     gy2=round(imu2.gyro.y)
#     gz2=round(imu2.gyro.z)
#     tem2=round(imu2.temperature,2)
    #print("ax",ax,"\t","ay",ay,"\t","az",az,"\t","gx",gx,"\t","gy",gy,"\t","gz",gz,"\t","Temperature",tem,"        ","\n","ax2",ax2,"\t","ay2",ay2,"\t","az2",az2,"\t","gx2",gx2,"\t","gy2",gy2,"\t","gz2",gz2,"\t","Temperature2",tem2,"        ",end="\r")
    
#     data_gyro2 = package_data(ax2, ay2, az2)
#  
#     tilt_x2, tilt_y2, tilt_z2 = calculate_tilt_angles(data_gyro2['accel'])


#     print("X Tilt 1: {:.2f} |||| X Tilt 2: {:.2f}".format(tilt_x1, tilt_x2))
#     print("Y Tilt 1: {:.2f} |||| Y Tilt 2: {:.2f}".format(tilt_y1, tilt_y2))
#     print("Z Tilt 1: {:.2f} |||| Z Tilt 2: {:.2f}".format(tilt_z1, tilt_z2))
    
#     diff_X = tilt_x1 - tilt_x2
#     diff_Y = tilt_y1 - tilt_y2
#     diff_Z = tilt_z1 - tilt_z2
    
#     print("Diff X: {:.2f} ||| Diff Y: {:.2f} ||| Diff Z: {:.2f},".format(diff_X, diff_Y, diff_Z), end="\r")
    
    output1=""
    if tilt_x1 < -30:
        output1+="Go Forward X: {:.2f},".format(tilt_x1)
    elif tilt_x1 > 30:
        output1+="Go Backward X: {:.2f},".format(tilt_x1)
    else:
        output1+="Stay X: {:.2f},".format(tilt_x1)
        
    if tilt_y1 < -15:
        output1+=" Turn Right Y: {:.2f},".format(tilt_y1)
    elif tilt_y1 > 15:
        output1+=" Turn Left Y: {:.2f},".format(tilt_y1)
    else:
        output1+=" Stay Y: {:.2f},".format(tilt_y1)
        
        
#     output2=""
#     if tilt_x2 < -30:
#         output2+="Go Forward X: {:.2f},".format(tilt_x2)
#     elif tilt_x2 > 30:
#         output2+="Go Backward X: {:.2f},".format(tilt_x2)
#     else:
#         output2+="Stay X: {:.2f},".format(tilt_x2)
#         
#     if tilt_y2 < -15:
#         output2+=" Turn Right Y: {:.2f},".format(tilt_y2)
#     elif tilt_y2 > 15:
#         output2+=" Turn Left Y: {:.2f},".format(tilt_y2)
#     else:
#         output2+=" Stay Y: {:.2f},".format(tilt_y2)
#
    print(output1,"|||| \t ||||", end="\r")
#     
    
    utime.sleep(1)


