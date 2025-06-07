"""Entry point for reading sensors and streaming the data."""
import asyncio
from sensor_server import SensorServer

if __name__ == "__main__":
    server = SensorServer()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        pass
