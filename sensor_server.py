import asyncio
import json
from datetime import datetime

import websockets
from smbus2 import SMBus

from hrm_extended import ExtendedHeartRateMonitor
from mlx90614 import MLX90614
from mpu6050 import mpu6050
# GreenPonik_BH1750 exposes a module named ``BH1750`` containing the class.
# Import the class explicitly to avoid treating the module itself as callable.
from GreenPonik_BH1750.BH1750 import BH1750
import bme680


class SensorServer:
    def __init__(self, bus=1, host="0.0.0.0", port=8765):
        self.bus = SMBus(bus)
        self.host = host
        self.port = port
        self.hrm = ExtendedHeartRateMonitor()
        self.temp_sensor = MLX90614(bus=self.bus)
        self.motion = mpu6050(0x68)
        self.light = BH1750()
        # The BME680 on the test setup uses address 0x77
        self.env = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
        self.clients = set()

        self.env.set_humidity_oversample(bme680.OS_2X)
        self.env.set_pressure_oversample(bme680.OS_4X)
        self.env.set_temperature_oversample(bme680.OS_8X)
        self.env.set_filter(bme680.FILTER_SIZE_3)

    async def handler(self, websocket):
        self.clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)

    def read_sensors(self):
        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "hr": self.hrm.bpm,
            "spo2": self.hrm.spo2,
            "object_temp": self.temp_sensor.get_obj_temp(),
            "ambient_temp": self.temp_sensor.get_amb_temp(),
            "accel": self.motion.get_accel_data(),
            "gyro": self.motion.get_gyro_data(),
            "lux": self.light.read_bh1750(),
            "temperature": self.env.data.temperature,
            "pressure": self.env.data.pressure,
            "humidity": self.env.data.humidity,
            "gas_resistance": self.env.data.gas_resistance,
        }
        return data

    async def broadcast(self):
        while True:
            data = self.read_sensors()
            message = json.dumps(data)
            for ws in list(self.clients):
                try:
                    await ws.send(message)
                except websockets.ConnectionClosed:
                    self.clients.remove(ws)
            await asyncio.sleep(0.5)

    async def start(self):
        self.hrm.start_sensor()
        async with websockets.serve(self.handler, self.host, self.port):
            await self.broadcast()
        self.hrm.stop_sensor()


if __name__ == "__main__":
    server = SensorServer()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        pass
