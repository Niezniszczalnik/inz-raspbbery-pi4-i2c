# Prosty serwer WebSocket zbierajacy dane z sensorow I2C
# Skrypt odczytuje parametry z kilku czujnikow i udostepnia je klientom
import asyncio
import json
import logging
from datetime import datetime
import socket
import subprocess

import websockets
from smbus2 import SMBus


def get_local_ip() -> str:
    """Return the best-effort local IP address."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
    except OSError:
        ip = "unknown"
    finally:
        sock.close()
    return ip


def get_wifi_ssid() -> str:
    """Return the Wi-Fi SSID if available."""
    try:
        return subprocess.check_output(["iwgetid", "-r"], text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""

logger = logging.getLogger(__name__)

from blood_oxygen_monitor import BloodOxygenMonitor
from mlx90614 import MLX90614
from mpu6050 import mpu6050

# Biblioteka GreenPonik_BH1750 udostepnia klase BH1750 w module o tej samej
# nazwie, wiec pobieramy ja jawnie.
from GreenPonik_BH1750.BH1750 import BH1750
import bme680


class SensorServer:
    # Klasa obsluguje czujniki i wysyla dane do klientow
    def __init__(self, bus=1, host="0.0.0.0", port=8765):
        # Inicjalizacja magistrali I2C oraz parametrow polaczenia WebSocket
        self.bus = SMBus(bus)
        self.host = host
        self.port = port
        self.ip_address = get_local_ip()
        self.wifi_ssid = get_wifi_ssid()
        self.hrm = BloodOxygenMonitor()
        self.temp_sensor = MLX90614(bus=self.bus)
        self.motion = mpu6050(0x68)
        self.light = BH1750()
        # BME680 pracuje pod adresem 0x77
        self.env = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
        self.clients = set()

        # Ustawiamy jakosc pomiaru srodowiskowego
        self.env.set_humidity_oversample(bme680.OS_2X)
        self.env.set_pressure_oversample(bme680.OS_4X)
        self.env.set_temperature_oversample(bme680.OS_8X)
        self.env.set_filter(bme680.FILTER_SIZE_3)

    async def handler(self, websocket):
        """Obsluga pojedynczego klienta WebSocket"""
        self.clients.add(websocket)
        try:
            info = json.dumps(
                {
                    "type": "info",
                    "ip": self.ip_address,
                    "wifi": self.wifi_ssid,
                    "message": "Serwer WebSocket uruchomiony",
                }
            )
            await websocket.send(info)
            await websocket.wait_closed()
                    finally:
            self.clients.remove(websocket)

    def read_sensors(self):
        """Czyta dane ze wszystkich sensorow"""
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Heart rate monitor values do not raise OSError
        hr = self.hrm.bpm
        spo2 = self.hrm.spo2

        try:
            object_temp = self.temp_sensor.get_obj_temp()
            ambient_temp = self.temp_sensor.get_amb_temp()
        except OSError as exc:
            logger.warning("MLX90614 read failed: %s", exc)
            object_temp = None
            ambient_temp = None

        try:
            accel = self.motion.get_accel_data()
        except OSError as exc:
            logger.warning("MPU6050 accel read failed: %s", exc)
            accel = {"x": 0, "y": 0, "z": 0}
    
        try:
            gyro = self.motion.get_gyro_data()
        except OSError as exc:
            logger.warning("MPU6050 gyro read failed: %s", exc)
            gyro = {"x": 0, "y": 0, "z": 0}

        try:
            lux = self.light.read_bh1750()
        except OSError as exc:
            logger.warning("BH1750 read failed: %s", exc)
            lux = None

        try:
            self.env.get_sensor_data()
            temperature = self.env.data.temperature
            pressure = self.env.data.pressure
            humidity = self.env.data.humidity
            gas_resistance = self.env.data.gas_resistance
        except OSError as exc:
            logger.warning("BME680 read failed: %s", exc)
            temperature = None
            pressure = None
            humidity = None
            gas_resistance = None

        data = {

        data = {
            "timestamp": timestamp,
            "hr": hr,
            "spo2": spo2,
            "object_temp": object_temp,
            "ambient_temp": ambient_temp,
            "accel": accel,
            "gyro": gyro,
            "lux": lux,
            "temperature": temperature,
            "pressure": pressure,
            "humidity": humidity,
            "gas_resistance": gas_resistance,
        }
        return data

    async def broadcast(self):
        """Wysyla pomiary do wszystkich klientow"""
        while True:
            data = self.read_sensors()
            message = json.dumps(data)
            for ws in list(self.clients):
                try:
                    await ws.send(message)
                    print("Wysylam pakiet do klienta")
                except websockets.ConnectionClosed:
                    self.clients.remove(ws)
            # Odczyt wykonywany co pol sekundy
            await asyncio.sleep(0.5)

    async def start(self):
        """Uruchamia serwer i watek HRM"""
        # Startujemy watek czujnika tetna
        self.hrm.start_sensor()
        try:
            print(
                f"WebSocket uruchomiony na {self.ip_address}, wifi: {self.wifi_ssid}"
            )
            async with websockets.serve(self.handler, self.host, self.port):
                await self.broadcast()
        finally:
            self.hrm.stop_sensor()
