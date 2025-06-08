# Raspberry Pi I2C Sensor Server

This repository contains a simple Python server for Raspberry Pi 4 that reads a set of I2C sensors and streams the measurements over a WebSocket connection. It is intended as a starting point for projects that combine IoT data with augmented reality devices such as the Epson BT-300.

## Supported sensors

- **MAX30102** pulse oximeter and heart‑rate sensor
- **MLX90614** infrared temperature sensor
- **MPU6050** 3‑axis accelerometer and gyroscope
- **BH1750** light sensor
- **BME680** environmental sensor (temperature, humidity, pressure and gas, address `0x77`)

## Installation

1. Enable the I2C interface on the Raspberry Pi using `raspi-config`.
2. Install system tools:
   ```bash
   sudo apt-get install -y i2c-tools python3-smbus
   ```
3. Install Python dependencies (preferably inside a virtual environment):
   ```bash
   pip install smbus2 numpy websockets PyMLX90614 mpu6050-raspberrypi bme680 GreenPonik-BH1750
   ```
   The repository also vendors a simple MAX30102 driver (`max30102.py`) and the original heart rate monitor helper (`heartrate_monitor.py`).
   A small wrapper (`hrm_extended.py`) adds SpO₂ tracking and is used by the WebSocket server started from `odczyt_sensory.py`.

## Usage

Run the WebSocket server with (adjust the path if you cloned the repository
elsewhere):

```bash
python3 /home/filip/Desktop/max30102/odczyt_sensory.py
```

The server listens on port `8765` and broadcasts a JSON message roughly twice per second containing the latest readings from all sensors. Connect from your application (for example a Unity app running on the BT‑300) using a WebSocket client and process the incoming JSON data.

## JSON message format

An example message looks like:

```json
{
  "timestamp": "2025-01-01T12:00:00Z",
  "hr": 72.5,
  "spo2": 98.3,
  "object_temp": 36.7,
  "ambient_temp": 25.1,
  "accel": {"x": 0.01, "y": -0.02, "z": 0.98},
  "gyro": {"x": 1.2, "y": -0.5, "z": 0.3},
  "lux": 120.0,
  "temperature": 24.9,
  "pressure": 1012.8,
  "humidity": 40.5,
  "gas_resistance": 8500.0
}
```

## Notes

The code was written for a Raspberry Pi 4 running Python 3. Make sure all sensors are properly connected to the I2C bus and have the expected addresses. Some sensors may require calibration or additional configuration depending on the manufacturer documentation.
The server assumes the BME680 uses address `0x77` (constant `bme680.I2C_ADDR_SECONDARY`).
