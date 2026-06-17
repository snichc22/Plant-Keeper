# Plant Keeper

MicroPython project for an ESP32 plant monitor.

It reads:

- soil moisture over ADC
- distance from a VL53L0X time-of-flight sensor over I2C

It can also publish readings and solenoid commands over MQTT.

## Files

- `boot.py` starts the app
- `plant_guard.py` runs Wi-Fi, MQTT, sensors, display, and solenoid control
- `moisture_sensor.py` reads and calculates soil wetness
- `tof_sensor.py` reads the distance sensor
- `mqtt_sensor.py` publishes sensor values when MQTT is enabled
- `config/` contains pins, MQTT settings, topics, and sensor calibration
- `libs/` contains bundled MicroPython drivers

## Config

Main settings are in `config/general.py`.

Wi-Fi is configured with:

```python
WIFI_SSID = "S-Campus-Students"
WIFI_ENABLED = True
WIFI_ENTERPRISE = True
```

Put the username and password in `config/secrets.py`.

Turn MQTT and the OLED display on or off with:

```python
MQTT_ENABLED = True
DISPLAY_ENABLED = True
```

Set either one to `False` to disable it.

Moisture and ToF sensor topics/settings are in `config/sensors/`.

## Run

Copy the project files to the ESP32, including:

- root `.py` files
- `config/`
- `libs/`

Then reset the board. `boot.py` imports `plant_guard.py`, which starts the loop.

## License

GPLv3. See `LICENSE`.
