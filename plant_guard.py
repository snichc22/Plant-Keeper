from machine import ADC, Pin, I2C
import network
import time
import libs.ssd1306 as ssd1306

import config.general as config
from umqtt.simple import MQTTClient

import moisture_sensor
import tof_sensor
import utils

# WLAN verbinden
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

def open_the_lid():
    Pin(config.SOLENOID).value(1)

def close_the_lid():
    Pin(config.SOLENOID).value(0)

print('WIFI: try to connect ...')
while not wlan.isconnected():
    time.sleep_ms(200)
    pass
print("WLAN connected:", wlan.ifconfig())

import socket

print(socket.getaddrinfo("sc.htl-kaindorf.at", 1883))

# MQTT verbinden
mqtt = MQTTClient("esp32-client",
                    config.MQTT_BROKER,
                    port=config.MQTT_PORT,
                    user=config.MQTT_USER,
                    password=config.MQTT_PASSWORD)

try:
    mqtt.connect()
    print("MQTT connected")
except Exception as e:
    print("MQTT Error: ", e)

print("SDA:", config.SDA_PIN)
print("SCL:", config.SCL_PIN)

i2c=I2C(0,sda=Pin(config.SDA_PIN), scl=Pin(config.SCL_PIN), freq=400000)

class OledDisplay:
    def __init__(
        self,
        i2c,
        mqtt,
        width=128,
        height=64,
        text_x=0,
        raw_value_y=16,
        percentage_y=26
    ):
        self.mqtt = mqtt
        self.lines = []
        self.text_x = text_x
        self.raw_value_y = raw_value_y
        self.percentage_y = percentage_y

        self.i2c = i2c
        self.oled = ssd1306.SSD1306_I2C(width, height, i2c)
        
        self.initial()
        
    def initial(self):
        print(f'init callback')
        self.mqtt.set_callback(self.mqtt_callback)
        self.mqtt.subscribe(b'VERT-SUSTAIN-Callback/moisture')
        
    def mqtt_callback(self, topic, msg):
        print(f'receive message: {topic.decode()} -> {msg.decode()}')

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
        
        
class Application:
    def __init__(
        self,
        sensor,
        tof,
#        display,
        mqtt,
        update_interval=5
    ):
        self.sensor = sensor
        self.tof = tof
#        self.display = display
        self.update_interval = update_interval
        self.mqtt = mqtt

    def update(self):
        raw_value, percentage = self.sensor.read()
        print(raw_value, percentage)
        #self.display.show(raw_value, percentage)
        print("Moisture: {}".format(raw_value))
        self.tof.read()

    def run(self):
        while True:
            self.mqtt.check_msg()
            self.update()
            time.sleep(self.update_interval)

tof = tof_sensor.TofSensor(
    config.TOPIC_LOCATION,
    config,
    mqtt,
    i2c
)

moisture = moisture_sensor.MoistureSensor(
    config.TOPIC_LOCATION,
    config,
    mqtt
)

#display = OledDisplay(
#    i2c,
#    mqtt,
#    width=128,
#    height=64
#)

app = Application(
    sensor=moisture,
    tof=tof,
#    display=display,
    mqtt=mqtt,
    update_interval=5
)

app.run()

