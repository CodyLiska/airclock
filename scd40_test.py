import time

from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection
from sensirion_i2c_scd import Scd4xI2cDevice

def main():
    with LinuxI2cTransceiver("/dev/i2c-1") as i2c_transceiver:
        scd4x = Scd4xI2cDevice(I2cConnection(i2c_transceiver))

        scd4x.stop_periodic_measurement()
        time.sleep(1)

        print(f"Serial: {scd4x.read_serial_number()}")

        scd4x.start_periodic_measurement()
        print("Waiting for measurements...")

        while True:
            time.sleep(5)
            co2, temperature, humidity = scd4x.read_measurement()
            print(
                f"CO2: {co2.co2} ppm | "
                f"Temp: {temperature.degrees_celsius:.2f}°C | "
                f"Humidity: {humidity.percent_rh:.2f}%"
            )

if __name__ == "__main__":
    main()
