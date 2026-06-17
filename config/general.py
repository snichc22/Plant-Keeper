SDA_PIN = 33
SCL_PIN = 32

WIFI_SSID = "meowphone"
WIFI_PASSWORD = "labricecat"

MQTT_ENABLED = False
MQTT_USER = "htl"
MQTT_BROKER = "sc.htl-kaindorf.at"
MQTT_PORT = 1883
MQTT_PASSWORD = "welc0m3"

TOPIC_LOCATION = "top"

SOLENOID = 34
SOLENOID_COMMAND_TOPIC = TOPIC_LOCATION + "/solenoid/set"
SOLENOID_STATUS_TOPIC = TOPIC_LOCATION + "/solenoid/status"

SOLENOID_ON_MESSAGES = ("on", "start", "open", "1", "true")
SOLENOID_OFF_MESSAGES = ("off", "stop", "close", "0", "false")
