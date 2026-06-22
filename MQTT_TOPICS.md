# MQTT Topics

Base topic:

```text
top
```

## Published Topics

| Topic | Payload | Source |
| --- | --- | --- |
| `top/moisture` | Raw moisture ADC value | `moisture_sensor.py` |
| `top/moisture/wetness` | Moisture percentage, formatted with 2 decimals | `moisture_sensor.py` |
| `top/tof` | Raw VL53L0X distance value | `tof_sensor.py` |
| `top/solenoid/status` | `on` or `off` | `plant_guard.py` |

## Subscribed Topics

| Topic | Accepted payloads | Source |
| --- | --- | --- |
| `top/solenoid/set` | `on`, `start`, `open`, `1`, `true` | `plant_guard.py` |
| `top/solenoid/set` | `off`, `stop`, `close`, `0`, `false` | `plant_guard.py` |

## Config Values

```python
TOPIC_LOCATION = "top"
SOLENOID_COMMAND_TOPIC = TOPIC_LOCATION + "/solenoid/set"
SOLENOID_STATUS_TOPIC = TOPIC_LOCATION + "/solenoid/status"
```

Sensor suffixes:

```python
# config/sensors/moisture.py
MQTT_TOPIC = "moisture"
MQTT_WETNESS_TOPIC = MQTT_TOPIC + "/wetness"

# config/sensors/tof.py
MQTT_TOPIC = "tof"
```
