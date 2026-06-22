SDA_PIN = 33
SCL_PIN = 32

WIFI_SSID = "S-Campus-Students"
WIFI_ENABLED = True
WIFI_ENTERPRISE = True
WIFI_USERNAME = ""
WIFI_PASSWORD = ""

try:
    from config.secrets import WIFI_USERNAME, WIFI_PASSWORD
except ImportError:
    pass

MQTT_ENABLED = True
MQTT_USER = "htl"
MQTT_BROKER = "sc.htl-kaindorf.at"
MQTT_PORT = 1883
MQTT_PASSWORD = "welc0m3"

try:
    import config.local as local_config
    MQTT_ENABLED = getattr(local_config, "MQTT_ENABLED", MQTT_ENABLED)
    MQTT_USER = getattr(local_config, "MQTT_USER", MQTT_USER)
    MQTT_BROKER = getattr(local_config, "MQTT_BROKER", MQTT_BROKER)
    MQTT_PORT = getattr(local_config, "MQTT_PORT", MQTT_PORT)
    MQTT_PASSWORD = getattr(local_config, "MQTT_PASSWORD", MQTT_PASSWORD)
except ImportError:
    pass

DISPLAY_ENABLED = False

TOPIC_LOCATION = "top"

SOLENOID = 12
SOLENOID_COMMAND_TOPIC = TOPIC_LOCATION + "/solenoid/set"
SOLENOID_STATUS_TOPIC = TOPIC_LOCATION + "/solenoid/status"

SOLENOID_ON_MESSAGES = ("on", "start", "open", "1", "true")
SOLENOID_OFF_MESSAGES = ("off", "stop", "close", "0", "false")
