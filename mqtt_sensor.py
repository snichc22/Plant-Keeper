class MqttSensor:
    def __init__(self, mqtt):
        self.mqtt = mqtt
    
    def send(self, topic, value):
        #self.mqtt.publish(self.to_bytes(topic), self.to_bytes(value), True)
        pass

    def to_bytes(self, value):
        pass
        #if isinstance(value, bytes):
        #    return value
        #return str(value).encode()
