"""Prosty program uruchamiajacy serwer z danymi z sensorow"""
# Plik wejsciowy uruchamiany na Raspberry Pi
import warnings
import asyncio
from sensor_server import SensorServer

# Adafruit Blinka on Linux tries to set the I2C frequency which is not
# supported. This produces a noisy RuntimeWarning. We silence that specific
# warning to avoid confusing users.
warnings.filterwarnings(
    "ignore",
    message="I2C frequency is not settable in python, ignoring!",
    category=RuntimeWarning,
    module="adafruit_blinka.microcontroller.generic_linux.i2c",
)

if __name__ == "__main__":
    # Tworzymy serwer i uruchamiamy petle glowna
    server = SensorServer()
    try:
        asyncio.run(server.start())  # startujemy serwer WebSocket
    except KeyboardInterrupt:
        pass  # zakonczenie programu klawiszem Ctrl+C
