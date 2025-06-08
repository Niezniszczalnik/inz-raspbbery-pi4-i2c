"""Prosty program uruchamiajacy serwer z danymi z sensorow"""
# Plik wejsciowy uruchamiany na Raspberry Pi
import asyncio
from sensor_server import SensorServer

if __name__ == "__main__":
    # Tworzymy serwer i uruchamiamy petle glowna
    server = SensorServer()
    try:
        asyncio.run(server.start())  # startujemy serwer WebSocket
    except KeyboardInterrupt:
        pass  # zakonczenie programu klawiszem Ctrl+C
