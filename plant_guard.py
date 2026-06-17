from machine import ADC, Pin, I2C
import network
import time
import libs.ssd1306 as ssd1306

import config.general as config
from umqtt.simple import MQTTClient

import config.sensors.moisture as moisture_config
import config.sensors.tof as tof_config
import moisture_sensor
import tof_sensor
import utils

# WLAN verbinden
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

print('WIFI: try to connect ...')
while not wlan.isconnected():
    time.sleep_ms(200)
    pass
print("WLAN connected:", wlan.ifconfig())

# MQTT verbinden
mqtt = MQTTClient("esp32-client",
                    config.MQTT_BROKER,
                    port=config.MQTT_PORT,
                    user=config.MQTT_USER,
                    password=config.MQTT_PASSWORD)

mqtt.connect()
print("MQTT connected")

i2c=I2C(0,sda=config.SDA_PIN, scl=config.SCL_PIN, freq=400000)

class OledDisplay:
    def __init__(
        self,
        i2c,
        width=128,
        height=64,
        text_x=0,
        raw_value_y=16,
        percentage_y=26
    ):
        self.lines = []
        self.text_x = text_x
        self.raw_value_y = raw_value_y
        self.percentage_y = percentage_y

        self.i2c = i2c
        self.oled = ssd1306.SSD1306_I2C(width, height, i2c)
        
        self.initial()
        
    def initial(self):
        print('init display')

    def add_line(self, line):
        self.lines.append(line);

    def show(self, raw_value, percentage):
        self.oled.fill(0)
        self.show_info_line()
        
        self.oled.text(f'Feuchte {percentage:.2f}%', self.text_x, self.percentage_y)
        self.oled.show()
        
    def show_info_line(self):
        actual_time = time.localtime(time.time())
        self.oled.text(f'{actual_time[3]:02d}:{actual_time[4]:02d}', 0, 0)
        num_rectangles = utils.rssi_to_int(wlan.status('rssi'))
        
        rectangle_height = 8
        num_rectangles = 4
        rectangle_width = 3  # Breite für die Rechtecke
        
        offset_signal_strength = 110
        for x in range(utils.rssi_to_int(wlan.status('rssi'))):
            self.oled.fill_rect(offset_signal_strength + x*5, 0, rectangle_width, rectangle_height, 1)
        

class SolenoidController:
    def __init__(
        self,
        mqtt,
        pin,
        command_topic,
        status_topic,
        on_messages,
        off_messages
    ):
        self.mqtt = mqtt
        self.pin = Pin(pin, Pin.OUT)
        self.command_topic = command_topic
        self.command_topic_bytes = command_topic.encode()
        self.status_topic = status_topic
        self.on_messages = on_messages
        self.off_messages = off_messages

        self.turn_off()

    def subscribe(self):
        self.mqtt.subscribe(self.command_topic_bytes)
        print("Subscribed to solenoid commands:", self.command_topic)

    def handle_message(self, topic, msg):
        if topic != self.command_topic_bytes:
            return False

        command = msg.decode().strip().lower()
        print("Solenoid command:", command)

        if command in self.on_messages:
            self.turn_on()
        elif command in self.off_messages:
            self.turn_off()
        else:
            print("Unknown solenoid command:", command)

        return True

    def turn_on(self):
        self.pin.value(1)
        self.publish_status("on")

    def turn_off(self):
        self.pin.value(0)
        self.publish_status("off")

    def publish_status(self, status):
        self.mqtt.publish(self.status_topic.encode(), status.encode(), True)
        
        
class Application:
    def __init__(
        self,
        sensor,
        tof,
        display,
        solenoid,
        mqtt,
        update_interval=5
    ):
        self.sensor = sensor
        self.tof = tof
        self.display = display
        self.solenoid = solenoid
        self.update_interval = update_interval
        self.update_interval_ms = update_interval * 1000
        self.mqtt = mqtt
        self.mqtt.set_callback(self.mqtt_callback)
        self.solenoid.subscribe()

    def mqtt_callback(self, topic, msg):
        if self.solenoid.handle_message(topic, msg):
            return

        print("Unhandled MQTT message: {} -> {}".format(topic.decode(), msg.decode()))

    def update(self):
        raw_value, percentage = self.sensor.read()
        self.display.show(raw_value, percentage)
        print("Moisture: {}".format(raw_value))
        self.tof.read()

    def run(self):
        last_update = time.ticks_ms() - self.update_interval_ms
        while True:
            self.mqtt.check_msg()
            now = time.ticks_ms()
            if time.ticks_diff(now, last_update) >= self.update_interval_ms:
                self.update()
                last_update = now
            time.sleep_ms(100)

tof = tof_sensor.TofSensor(
    config.TOPIC_LOCATION,
    tof_config,
    mqtt,
    i2c
)

moisture = moisture_sensor.MoistureSensor(
    config.TOPIC_LOCATION,
    moisture_config,
    mqtt
)

display = OledDisplay(
    i2c,
    width=128,
    height=64
)

solenoid = SolenoidController(
    mqtt,
    config.SOLENOID,
    config.SOLENOID_COMMAND_TOPIC,
    config.SOLENOID_STATUS_TOPIC,
    config.SOLENOID_ON_MESSAGES,
    config.SOLENOID_OFF_MESSAGES
)

app = Application(
    sensor=moisture,
    tof=tof,
    display=display,
    solenoid=solenoid,
    mqtt=mqtt,
    update_interval=5
)

app.run()
