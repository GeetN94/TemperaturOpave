from machine import Pin
from onewire import OneWire
from ds18x20 import DS18X20
import time

# Data wire is connected to the ESP32 GPIO 4
ONE_WIRE_BUS = 4

# Setup a OneWire instance to communicate with any OneWire devices
ow = OneWire(Pin(ONE_WIRE_BUS))
# Pass our OneWire reference to DS18X20 temperature sensor
sensors = DS18X20(ow)

# Function to get temperature in Celsius and Fahrenheit
def get_temperature():
    # Scan for DS18X20 devices on the bus
    roms = ow.scan()

    if not roms:
        print("No DS18X20 devices found.")
        return

    # Request temperature conversion for all devices on the bus
    sensors.convert_temp()

    # Wait for temperature conversion to complete (750ms for DS18X20)
    time.sleep_ms(750)

    # Read and print temperature for each device
    for rom in roms:
        temperature_celsius = sensors.read_temp(rom)
        temperature_fahrenheit = temperature_celsius * 9/5 + 32

        print("Device {}: Celsius temperature: {:.2f}, Fahrenheit temperature: {:.2f}".format(rom, temperature_celsius, temperature_fahrenheit))

# Main loop
while True:
    get_temperature()
    time.sleep(1)