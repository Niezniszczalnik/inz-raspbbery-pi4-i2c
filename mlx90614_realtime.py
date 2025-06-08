import time
import warnings
from smbus2 import SMBus
from mlx90614 import MLX90614

# Suppress noisy warning on Linux when I2C frequency cannot be changed
warnings.filterwarnings(
    "ignore",
    message="I2C frequency is not settable in python, ignoring!",
    category=RuntimeWarning,
    module="adafruit_blinka.microcontroller.generic_linux.i2c",
)


def main():
    """Continuously print object and ambient temperature."""
    with SMBus(1) as bus:
        sensor = MLX90614(bus=bus)
        try:
            while True:
                obj = sensor.get_obj_temp()
                amb = sensor.get_amb_temp()
                print(f"Object: {obj:.2f} \u00b0C, Ambient: {amb:.2f} \u00b0C")
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
