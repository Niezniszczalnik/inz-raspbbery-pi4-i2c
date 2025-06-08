import time
import warnings
import argparse

from hrm_extended import ExtendedHeartRateMonitor

warnings.filterwarnings(
    "ignore",
    message="I2C frequency is not settable in python, ignoring!",
    category=RuntimeWarning,
    module="adafruit_blinka.microcontroller.generic_linux.i2c",
)


def main() -> None:
    """Run a simple monitor printing BPM/SpO2 from the MAX30102."""
    parser = argparse.ArgumentParser(description="Test MAX30102 sensor")
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print raw IR/Red values instead of interpreted results",
    )
    args = parser.parse_args()

    hrm = ExtendedHeartRateMonitor(print_raw=args.raw, print_result=not args.raw)
    hrm.start_sensor()
    try:
        while True:
            print(f"BPM: {hrm.bpm:.1f}, SpO2: {hrm.spo2:.1f}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        hrm.stop_sensor()


if __name__ == "__main__":
    main()
