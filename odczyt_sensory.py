"""Prosty program uruchamiajacy serwer z danymi z sensorow"""
import asyncio
from sensor_server import SensorServer

if __name__ == "__main__":
    # Tworzymy serwer i uruchamiamy petle glowna
    server = SensorServer()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        pass
