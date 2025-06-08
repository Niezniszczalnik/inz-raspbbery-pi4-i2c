from DFRobot_BloodOxygen_S import DFRobot_BloodOxygen_S_i2c
import threading
import time


class BloodOxygenMonitor:
    """Threaded reader for the SEN0518 blood oxygen sensor."""

    LOOP_TIME = 0.2

    def __init__(self, bus: int = 1, address: int = 0x20) -> None:
        self.sensor = DFRobot_BloodOxygen_S_i2c(bus, address=0x57)
        if not self.sensor.begin():
            raise RuntimeError("Failed to initialize the blood oxygen sensor")
        self.bpm = 0
        self.spo2 = 0

    def run_sensor(self) -> None:
        self.sensor.sensor_start_collect()
        while not self._thread.stopped:
            try:
                self.sensor.get_heartbeat_SPO2()
                self.bpm = self.sensor.heartbeat if self.sensor.heartbeat >= 0 else 0
                self.spo2 = self.sensor.SPO2 if self.sensor.SPO2 >= 0 else 0
            except Exception:
                pass
            time.sleep(self.LOOP_TIME)
        self.sensor.sensor_end_collect()

    def start_sensor(self) -> None:
        self._thread = threading.Thread(target=self.run_sensor)
        self._thread.stopped = False
        self._thread.start()

    def stop_sensor(self, timeout: float = 2.0) -> None:
        self._thread.stopped = True
        self._thread.join(timeout)
        self.bpm = 0
        self.spo2 = 0
