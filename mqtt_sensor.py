class MqttSensor:
    def __init__(self, mqtt):
        self.mqtt = mqtt
    
    def send(self, topic, value):
        full_topic = topic
        self.mqtt.publish(full_topic, str(value), True)
