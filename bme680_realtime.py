import time
import warnings
import bme680

warnings.filterwarnings(
    "ignore",
    message="I2C frequency is not settable in python, ignoring!",
    category=RuntimeWarning,
    module="adafruit_blinka.microcontroller.generic_linux.i2c",
)


def main():
    """Continuously print environment data from the BME680 sensor."""
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
    sensor.set_humidity_oversample(bme680.OS_2X)
    sensor.set_pressure_oversample(bme680.OS_4X)
    sensor.set_temperature_oversample(bme680.OS_8X)
    sensor.set_filter(bme680.FILTER_SIZE_3)

    try:
        while True:
            sensor.get_sensor_data()
            temp = sensor.data.temperature
            press = sensor.data.pressure
            hum = sensor.data.humidity
            gas = sensor.data.gas_resistance
            print(
                f"Temp: {temp:.2f} \u00b0C, Pressure: {press:.2f} hPa, "
                f"Humidity: {hum:.2f} %, Gas: {gas:.2f} \u03a9"
            )
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
