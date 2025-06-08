# Rozszerzony monitor tetna oparty na bibliotece MAX30102
from max30102 import MAX30102
import hrcalc
import threading
import time
import numpy as np

# Minimal average signal level required to treat a reading as valid
FINGER_DETECT_THRESHOLD = 10000


class ExtendedHeartRateMonitor:
    """Watek odczytujacy BPM i SpO2 z czujnika"""

    LOOP_TIME = 0.01  # opoznienie miedzy kolejnymi iteracjami petli

    def __init__(self, print_raw: bool = False, print_result: bool = False):
        """Tworzy obiekt i ustawia opcje debugowania"""
        self.bpm = 0
        self.spo2 = 0
        if print_raw:
            print("IR, Red")
        self.print_raw = print_raw
        self.print_result = print_result

    def run_sensor(self):
        """Glowna petla odczytu danych"""
        sensor = MAX30102()
        ir_data = []  # surowe wartosci IR
        red_data = []  # surowe wartosci czerwonego swiatla
        bpms = []      # bufor ostatnich pomiarow tetna

        while not self._thread.stopped:
            num_bytes = sensor.get_data_present()  # ile pomiarow czeka w buforze
            if num_bytes > 0:
                while num_bytes > 0:
                    red, ir = sensor.read_fifo()
                    num_bytes -= 1
                    ir_data.append(ir)
                    red_data.append(red)
                    if self.print_raw:
                        print(f"{ir}, {red}")

                while len(ir_data) > 100:
                    ir_data.pop(0)
                    red_data.pop(0)

                if len(ir_data) == 100:
                    # Obliczamy tetno i SpO2 z ostatnich 100 probek
                    bpm, valid_bpm, spo2, valid_spo2 = hrcalc.calc_hr_and_spo2(ir_data, red_data)
                    if valid_bpm:
                        bpms.append(bpm)
                        while len(bpms) > 4:
                            bpms.pop(0)
                        self.bpm = np.mean(bpms)
                        if (
                            np.mean(ir_data) < FINGER_DETECT_THRESHOLD
                            and np.mean(red_data) < FINGER_DETECT_THRESHOLD
                        ):
                            self.bpm = 0
                            if self.print_result:
                                print("Finger not detected")
                        if self.print_result:
                            print(f"BPM: {self.bpm}, SpO2: {spo2}")
                    if valid_spo2:
                        self.spo2 = spo2

            # Krotka pauza dla stabilnej pracy watku
            time.sleep(self.LOOP_TIME)
            
        sensor.shutdown()

    def start_sensor(self):
        """Uruchamia watek pomiaru"""
        # Tworzymy i uruchamiamy watek z odczytem czujnika
        self._thread = threading.Thread(target=self.run_sensor)
        self._thread.stopped = False
        self._thread.start()

    def stop_sensor(self, timeout: float = 2.0):
        """Zatrzymuje watek pomiaru"""
        # Sygnal zatrzymania i porzadkowanie danych
        self._thread.stopped = True
        self.bpm = 0
        self.spo2 = 0
        self._thread.join(timeout)
