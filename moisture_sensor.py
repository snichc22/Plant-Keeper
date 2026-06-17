import mqtt_sensor

from machine import ADC, Pin, I2C

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
        percentage = 100 - ((self.dry_value - value) / (self.dry_value - self.wet_value)) * 100
        #super(MoistureSensor, self).send(self.main_topic + '/' + self.config.MOISTURE, str(value))
        return value, percentage
    
    def send_mqtt(self):
        pass