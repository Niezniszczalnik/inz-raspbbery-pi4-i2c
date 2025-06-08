import time
import warnings
from mpu6050 import mpu6050

warnings.filterwarnings(
    "ignore",
    message="I2C frequency is not settable in python, ignoring!",
    category=RuntimeWarning,
    module="adafruit_blinka.microcontroller.generic_linux.i2c",
)


def main():
    """Continuously print accelerometer and gyroscope data."""
    sensor = mpu6050(0x68)
    try:
        while True:
            accel = sensor.get_accel_data()
            gyro = sensor.get_gyro_data()
            print(f"Accel: {accel}, Gyro: {gyro}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
