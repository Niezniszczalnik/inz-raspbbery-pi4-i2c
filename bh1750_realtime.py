import time
import warnings
from GreenPonik_BH1750.BH1750 import BH1750

warnings.filterwarnings(
    "ignore",
    message="I2C frequency is not settable in python, ignoring!",
    category=RuntimeWarning,
    module="adafruit_blinka.microcontroller.generic_linux.i2c",
)


def main():
    """Continuously print light intensity in lux."""
    sensor = BH1750()
    try:
        while True:
            lux = sensor.read_bh1750()
            print(f"Lux: {lux}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
