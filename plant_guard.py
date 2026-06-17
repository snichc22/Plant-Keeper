from machine import Pin, I2C
import network
import time

import config.general as config
import config.sensors.moisture as moisture_config
import config.sensors.tof as tof_config
import moisture_sensor
import tof_sensor
import utils

MQTTClient = None
ssd1306 = None

if config.MQTT_ENABLED:
    try:
        from umqtt.simple import MQTTClient
    except ImportError:
        from libs.umqttsimple import MQTTClient

if config.DISPLAY_ENABLED:
    import libs.ssd1306 as ssd1306


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

    print("WIFI: try to connect ...")
    while not wlan.isconnected():
        time.sleep_ms(200)

    print("WLAN connected:", wlan.ifconfig())
    return wlan


def connect_mqtt():
    if not config.MQTT_ENABLED:
        print("MQTT disabled")
        return None

    mqtt = MQTTClient(
        "esp32-client",
        config.MQTT_BROKER,
        port=config.MQTT_PORT,
        user=config.MQTT_USER,
        password=config.MQTT_PASSWORD
    )

    mqtt.connect()
    print("MQTT connected")
    return mqtt


wlan = None
mqtt = None

if config.MQTT_ENABLED:
    wlan = connect_wifi()
    try:
        mqtt = connect_mqtt()
    except Exception as e:
        print("MQTT Error:", e)
        mqtt = None

i2c = I2C(0, sda=Pin(config.SDA_PIN), scl=Pin(config.SCL_PIN), freq=400000)


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
        print("init display")

    def add_line(self, line):
        self.lines.append(line)

    def show(self, raw_value, percentage):
        self.oled.fill(0)
        self.show_info_line()

        self.oled.text("Feuchte {:.2f}%".format(percentage), self.text_x, self.percentage_y)
        self.oled.show()

    def show_info_line(self):
        actual_time = time.localtime(time.time())
        self.oled.text("{:02d}:{:02d}".format(actual_time[3], actual_time[4]), 0, 0)

        if wlan is None or not wlan.isconnected():
            return

        rectangle_height = 8
        rectangle_width = 3
        offset_signal_strength = 110

        for x in range(utils.rssi_to_int(wlan.status("rssi"))):
            self.oled.fill_rect(
                offset_signal_strength + x * 5,
                0,
                rectangle_width,
                rectangle_height,
                1
            )


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
        if self.mqtt is None:
            return

        self.mqtt.subscribe(self.command_topic_bytes)
        print("Subscribed to solenoid commands:", self.command_topic)

    def handle_message(self, topic, msg):
        if self.mqtt is None:
            return False

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
        if self.mqtt is None:
            return

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

        if self.mqtt is not None:
            self.mqtt.set_callback(self.mqtt_callback)

        self.solenoid.subscribe()

    def mqtt_callback(self, topic, msg):
        if self.solenoid.handle_message(topic, msg):
            return

        print("Unhandled MQTT message: {} -> {}".format(topic.decode(), msg.decode()))

    def update(self):
        raw_value, percentage = self.sensor.read()
        if self.display is not None:
            self.display.show(raw_value, percentage)
        print("Moisture: {}".format(raw_value))
        self.tof.read()

    def run(self):
        last_update = time.ticks_ms() - self.update_interval_ms
        while True:
            if self.mqtt is not None:
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

display = None

if config.DISPLAY_ENABLED:
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
