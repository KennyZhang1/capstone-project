import RTIMU
import sys

SETTINGS_FILE = "RTIMULib"

if not RTIMU.SettingsExists(SETTINGS_FILE):
    print("Settings file does not exist.")
    sys.exit(1)

imu = RTIMU.RTIMU(SETTINGS_FILE)
imu.IMUInit()

if not imu.IMUInit():
    print("IMU Init Failed.")
    sys.exit(1)

imu.setSlerpPower(0.02)
imu.setGyroEnable(True)
imu.setAccelEnable(True)
imu.setCompassEnable(True)

poll_interval = imu.IMUGetPollInterval()

while True:
    if imu.IMURead():
        data = imu.getIMUData()
        fusionPose = data["fusionPose"]
        yaw = fusionPose[2]  # Z-axis angle (yaw)
        print("Yaw Angle:", yaw)
