import mqtt_sensor

from machine import ADC, Pin

class MoistureSensor(mqtt_sensor.MqttSensor):
    def __init__(
        self,
        main_topic,
        config,
        mqtt
    ):
        super().__init__(mqtt)
        self.config = config
        self.main_topic = main_topic
        self.dry_value = config.MOISTURE_DRY_MAX
        self.wet_value = config.MOISTURE_WET_MAX

        print(f'pin {config.MOISTURE_ADC_PIN}')
        self.sensor = ADC(Pin(self.config.MOISTURE_ADC_PIN))
        self.sensor.width(ADC.WIDTH_12BIT)
        self.sensor.atten(ADC.ATTN_11DB)

    def read_raw_value(self):
        return self.sensor.read()

    def read(self):
        value = self.read_raw_value()
        wetness = self.calculate_wetness(value)
        self.send_mqtt(value, wetness)
        return value, wetness

    def calculate_wetness(self, value):
        span = self.wet_value - self.dry_value
        if span == 0:
            return 0

        wetness = ((value - self.dry_value) / span) * 100
        if wetness < 0:
            return 0
        if wetness > 100:
            return 100
        return wetness

    def send_mqtt(self, raw_value, wetness):
        base_topic = self.main_topic + '/' + self.config.MQTT_TOPIC
        super(MoistureSensor, self).send(base_topic, str(raw_value))
        super(MoistureSensor, self).send(self.main_topic + '/' + self.config.MQTT_WETNESS_TOPIC, "{:.2f}".format(wetness))
