import mqtt_sensor

from machine import ADC, Pin, I2C
import libs.vl53l0x as vl53l0x

class TofSensor(mqtt_sensor.MqttSensor):
    def __init__(
        self,
        main_topic,
        config,
        mqtt,
        i2c
    ):
        super().__init__(mqtt)
        self.main_topic = main_topic
        self.config = config
        self.sensor = vl53l0x.VL53L0X(i2c)

    def read_raw_value(self):
        return self.sensor.read()

    def read(self):
        value = self.read_raw_value()
        print(f'Value: {value}')
        percentage = 1 - ((200 - value) / 200) # 200cm max range
        #self.send_mqtt(value)
        return value, percentage
    
    def send_mqtt(self, value):
        #super(TofSensor, self).send(self.main_topic + '/' + self.config.TOF, str(value))
        pass
       