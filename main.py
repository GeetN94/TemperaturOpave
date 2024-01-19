from machine import Pin
from onewire import OneWire
from ds18x20 import DS18X20
import time
import network
import socket
import gc

ONE_WIRE_BUS = 4

sensor_names = {
    '283ecf9d0b000007': 'Temperature Sensor 1',
    '2877109b0b0000cb': 'Temperature Sensor 2',
    # Add more sensors as needed
}

ow = OneWire(Pin(ONE_WIRE_BUS))
ds_sensor = DS18X20(ow)


def read_ds_sensors():
    roms = ow.scan()

    if not roms:
        return ["No DS18X20 devices found."]

    ds_sensor.convert_temp()
    time.sleep_ms(750)

    temperatures = []

    for rom in roms:
        temp_celsius = ds_sensor.read_temp(rom)
        temp_fahrenheit = temp_celsius * 9/5 + 32
        sensor_name = sensor_names.get(rom.hex(), 'Sensor 1')

        temperatures.append(
            {"sensor_name": sensor_name, "temperature_celsius": temp_celsius, "temperature_fahrenheit": temp_fahrenheit}
        )

    return temperatures


def web_page():
    temperatures = read_ds_sensors()

    html = """<!DOCTYPE HTML><html><head>
    <style>
        body {"""
    
    if len(temperatures) >= 2:
        temp_diff = temperatures[0]["temperature_celsius"] - temperatures[1]["temperature_celsius"]

        html += f"""
            background-color: {'red' if abs(temp_diff) > 4 else 'white'};
        """
    
    html += """}
    </style>
    <!-- Some CSS styles are included -->
    </head><body><h2>ESP with DS18X20</h2>"""

    if len(temperatures) >= 2:
        html += f"""<p><i class="fas fa-thermometer-half" style="color:#059e8a;"></i> 
            <span class="ds-labels">{temperatures[0]["sensor_name"]}</span>
            <span id="temperature1"> {temperatures[0]["temperature_celsius"]:.2f}</span>
            <sup class="units">&deg;C</sup>
        </p>
        <p><i class="fas fa-thermometer-half" style="color:#059e8a;"></i> 
            <span class="ds-labels">{temperatures[1]["sensor_name"]}</span>
            <span id="temperature2"> {temperatures[1]["temperature_celsius"]:.2f}</span>
            <sup class="units">&deg;C</sup>
        </p>
        <p><strong>Temperature Difference:</strong> {temp_diff:.2f} &deg;C</p>"""
    else:
        html += "<p>No data available for two sensors.</p>"

    html += """</body></html>"""

    return html


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    try:
        if gc.mem_free() < 102000:
            gc.collect()
        conn, addr = s.accept()
        conn.settimeout(3.0)
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        conn.settimeout(None)
        request = str(request)
        print('Content = %s' % request)
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
    except OSError as e:
        conn.close()
        print('Connection closed')
