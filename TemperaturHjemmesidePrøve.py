from machine import Pin
from onewire import OneWire
from ds18x20 import DS18X20
import time
import network
from microdot import Microdot

# Data wire is connected to the ESP32 GPIO 4
ONE_WIRE_BUS = 4

# Sensor names and their corresponding addresses (converted to strings)
sensor_names = {
    '283ecf9d0b000007': 'Måler1',
    '2877109b0b0000cb': 'Måler2',
    # Add more sensors as needed
}

# Setup a OneWire instance to communicate with any OneWire devices
ow = OneWire(Pin(ONE_WIRE_BUS))
# Pass our OneWire reference to DS18X20 temperature sensor
sensors = DS18X20(ow)

# Function to get temperature in Celsius and Fahrenheit
def get_temperature():
    # Scan for DS18X20 devices on the bus
    roms = ow.scan()

    if not roms:
        return "No DS18X20 devices found."

    # Request temperature conversion for all devices on the bus
    sensors.convert_temp()

    # Wait for temperature conversion to complete (750ms for DS18X20)
    time.sleep_ms(750)

    temperature_data = []
    # Read and collect temperature for each device
    for rom in roms:
        temperature_celsius = sensors.read_temp(rom)
        temperature_fahrenheit = temperature_celsius * 9/5 + 32

        # Get the sensor name from the dictionary
        sensor_name = sensor_names.get(rom.hex(), 'Måler 1')

        temperature_data.append(
            "{}: Celsius temperature: {:.2f}, Fahrenheit temperature: {:.2f}".format(sensor_name, temperature_celsius, temperature_fahrenheit)
        )

    return temperature_data

# Create a Microdot App instance
app = Microdot()

# Define a route for handling HTTP requests
@app.route('/temperature')
def temperature_handler(request):
    temperature_data = get_temperature()
    content = "<html><body><h1>Temperature Readings</h1><p>{}</p></body></html>".format("<br>".join(temperature_data))
    return content

# Connect to Wi-Fi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("WhyFy_XXX_Tentacleon", "PFRRDJK8XH")

while not wifi.isconnected():
    pass

# ...
# Wait until connected
while not wifi.isconnected():
    pass
    
# Print the device's IP address
device_ip = wifi.ifconfig()[0]
print("Device IP address:", device_ip)

# Start the Microdot App
app.run(debug=True, host=device_ip, port=2000)