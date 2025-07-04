
# inz-raspbbery-pi4-i2c
# Raspberry Pi I2C Sensor Server

This repository contains a simple Python server for Raspberry Pi 4 that reads a set of I2C sensors and streams the measurements over a WebSocket connection. It is intended as a starting point for projects that combine IoT data with augmented reality devices such as the Epson BT-300.

## Supported sensors

- **MAX30102** – pulsoksymetr i czujnik tętna
- **MLX90614** – bezkontaktowy czujnik temperatury na podczerwień
- **MPU6050** – inercyjny sensor 6DOF
- **BH1750** – czujnik natężenia oświetlenia (luxometr)
- **BME680** – wielofunkcyjny czujnik środowiskowy (domyślnie adres `0x77`)

## Installation

1. Enable the I2C interface on the Raspberry Pi using `raspi-config`.
2. Install system tools:
   ```bash
   sudo apt-get install -y i2c-tools python3-smbus
   ```
3. Install Python dependencies (preferably inside a virtual environment):
   ```bash
          pip install smbus2 numpy websockets PyMLX90614 mpu6050-raspberrypi bme680 GreenPonik-BH1750 pyserial
   ```
   The repository now vendors the DFRobot_BloodOxygen_S driver for the SEN0518 module
   (`DFRobot_BloodOxygen_S.py` and `DFRobot_RTU.py`). Heart rate and SpO₂ values
   are obtained directly using this driver in `sensor_server.py`.

## Usage

Run the WebSocket server with (adjust the path if you cloned the repository
elsewhere):

```bash
python3 /home/filip/Desktop/max30102/odczyt_sensory.py
```

The `BloodOxygenMonitor` class will automatically scan common I2C addresses
(0x57, 0x56, 0x55) and pick the first sensor that responds.  If your module uses
a different address you can pass it explicitly:

```python
from blood_oxygen_monitor import BloodOxygenMonitor
monitor = BloodOxygenMonitor(address=0x57)
```

The server listens on port `8765` and broadcasts a JSON message roughly twice per second containing the latest readings from all sensors. Connect from your application (for example a Unity app running on the BT‑300) using a WebSocket client and process the incoming JSON data.

## Simple HRM example

If you only want to quickly check the heart rate sensor you can run the
`max30102_realtime.py` script:

```bash
python3 max30102_realtime.py
```

It will print the BPM and SpO₂ values every half second until you press
`Ctrl+C`.

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
The server assumes the BME680 uses address `0x77` (constant `bme680.I2C_ADDR_SECONDARY`)

## Continuous integration

A simple GitHub Actions workflow installs the dependencies from
`requirements.txt` and runs `pytest` on a tiny test that imports all
project modules. This ensures that the sources remain syntactically
correct and that all imports resolve.
