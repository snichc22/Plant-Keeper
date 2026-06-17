class MqttSensor:
    def __init__(self, mqtt):
        self.mqtt = mqtt
    
    def send(self, topic, value):
        if self.mqtt is None:
            return

        self.mqtt.publish(self.to_bytes(topic), self.to_bytes(value), True)

    def to_bytes(self, value):
        if isinstance(value, bytes):
            return value
        return str(value).encode()
