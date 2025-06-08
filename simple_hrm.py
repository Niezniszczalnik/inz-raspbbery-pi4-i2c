import time
import warnings

from blood_oxygen_monitor import BloodOxygenMonitor

# Suppress noisy warning on Linux when I2C frequency cannot be changed
warnings.filterwarnings(
    "ignore",
    message="I2C frequency is not settable in python, ignoring!",
    category=RuntimeWarning,
    module="adafruit_blinka.microcontroller.generic_linux.i2c",
)


def main():
    """Continuously print heart rate and SpO2 readings."""
    monitor = BloodOxygenMonitor()
    monitor.start_sensor()
    try:
        while True:
            print(f"BPM: {monitor.bpm:.1f}, SpO2: {monitor.spo2:.1f}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop_sensor()


if __name__ == "__main__":
    main()
