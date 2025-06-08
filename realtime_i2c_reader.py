import json
import threading
import time
import warnings

from sensor_server import SensorServer

warnings.filterwarnings(
    "ignore",
    message="I2C frequency is not settable in python, ignoring!",
    category=RuntimeWarning,
    module="adafruit_blinka.microcontroller.generic_linux.i2c",
)


stop_event = threading.Event()


def _wait_for_exit():
    """Waits for the user to press Enter and then sets the stop flag."""
    input("Press ENTER to stop\n")
    stop_event.set()


def group_by_sensor(data):
    """Return nested dict grouping values by descriptive sensor name."""
    return {
        "timestamp": data.get("timestamp"),
        "MAX30102 - pulsoksymetr i czujnik tetna": {
            "hr": data.get("hr"),
            "spo2": data.get("spo2"),
        },
        "MLX90614 - bezkontaktowy czujnik temperatury na podczerwien": {
            "object_temp": data.get("object_temp"),
            "ambient_temp": data.get("ambient_temp"),
        },
        "MPU-6050 - inercyjny sensor 6DOF": {
            "accel": data.get("accel"),
            "gyro": data.get("gyro"),
        },
        "BH1750 - czujnik natezenia oswietlenia (luxometr)": {
            "lux": data.get("lux"),
        },
        "BME680 - wielofunkcyjny czujnik srodowiskowy": {
            "temperature": data.get("temperature"),
            "pressure": data.get("pressure"),
            "humidity": data.get("humidity"),
            "gas_resistance": data.get("gas_resistance"),
        },
    }


def main():
    server = SensorServer()
    server.hrm.start_sensor()

    # Start a background thread waiting for the user to stop the script
    threading.Thread(target=_wait_for_exit, daemon=True).start()

    try:
        while not stop_event.is_set():
            raw = server.read_sensors()
            grouped = group_by_sensor(raw)
            print(json.dumps(grouped, indent=2, ensure_ascii=False))
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.hrm.stop_sensor()


if __name__ == "__main__":
    main()
