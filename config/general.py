SDA_PIN = 19
SCL_PIN = 18

WIFI_SSID = "meowphone"
WIFI_PASSWORD = "labricecat"

MQTT_ENABLED = True
MQTT_USER = "mqttuser"
MQTT_BROKER = "192.168.194.117"
MQTT_PORT = 1883
MQTT_PASSWORD = "password"

TOPIC_LOCATION = "top"

SOLENOID = 0
SOLENOID_COMMAND_TOPIC = TOPIC_LOCATION + "/solenoid/set"
SOLENOID_STATUS_TOPIC = TOPIC_LOCATION + "/solenoid/status"

SOLENOID_ON_MESSAGES = ("on", "start", "open", "1", "true")
SOLENOID_OFF_MESSAGES = ("off", "stop", "close", "0", "false")
