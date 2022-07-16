import utime
from machine import Pin, I2C
import ahtx0
import network
import urequests as requests
from secrets import secrets
import sys
from mqtt import MQTTClient
from config import feed_config

def get_wlan_status(wlan):
    # Make sense of the wlan.status() numbers that are returned
    status = wlan.status()
    if status == network.STAT_IDLE:
        return 'STAT_IDLE'
    elif status == network.STAT_CONNECTING:
        return 'STAT_CONNECTING'
    elif status == network.STAT_WRONG_PASSWORD:
        return 'STAT_WRONG_PASSWORD'
    elif status == network.STAT_NO_AP_FOUND:
        return 'STAT_NO_AP_FOUND'
    elif status == network.STAT_CONNECT_FAIL:
        return 'STAT_CONNECT_FAIL'
    elif status == network.STAT_GOT_IP:
        return 'STAT_GOT_IP'
    else:
        return "Unknown wlan status: {}".format(status) 

def sub_cb(topic, msg):
    # Callback from MQTT
    print(msg)

# Set-up the I2C bus and add an AHT20 sensor to it
i2c = I2C(id=0, scl=Pin(21), sda=Pin(20))
sensor = ahtx0.AHT20(i2c)

# Define network and connect
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets["ssid"], secrets["password"])

# Define onboard LED
led_onboard = machine.Pin("LED", machine.Pin.OUT)

# Try to connect to wifi and flash the LED while you're doing it
# Define waiting index to limit the number of wifi re-connect attempts
max_wait = 20
while max_wait > 0:
    led_onboard.toggle()

    if wlan.isconnected():
        print("Connected to wifi")
        # Solid LED means the Pico has connected to wifi
        led_onboard.on()
        break

    max_wait -= 1
    print("Waiting for connection... (" + get_wlan_status(wlan) + ")")
    utime.sleep(1)

# Set-up MQTT client
client = MQTTClient(
    feed_config["feed_prefix"],
    "io.adafruit.com",
    user=secrets["adafruit_io_username"],
    password=secrets["adafruit_io_key"],
    port=1883
)
client.set_callback(sub_cb)

# Connect to MQTT server
client.connect()

topic_temperature = secrets["adafruit_io_username"] + "/feeds/" + feed_config["feed_prefix"] + "_temperature"
topic_humidity = secrets["adafruit_io_username"] + "/feeds/" + feed_config["feed_prefix"] + "_humidity"

client.subscribe(topic=topic_temperature)
client.subscribe(topic=topic_humidity)

# Main control loop
while True:
    # Print the readings so we've got something on the REPL monitor
    print("\nTemperature: %0.2f C" % sensor.temperature)
    print("Humidity: %0.2f %%" % sensor.relative_humidity)
    
    # Make sure wlan is connected before we send to AdafruitIO
    if wlan.isconnected():
        # Publish to MQTT at AdafruitIO
        print("\nPublishing to MQTT")
        client.publish(topic=topic_temperature, msg=str(sensor.temperature))
        client.publish(topic=topic_humidity, msg=str(sensor.relative_humidity))

    else:
        # Try and re-connect to wifi
        print("Disconnected from wifi")
        led_onboard.off()
        wlan.disconnect()
        wlan.connect(secrets["ssid"], secrets["password"])
        
        if wlan.isconnected():
            print("Re-connected to wifi")
            led_onboard.on()
        else:
            print("Failed to re-connect to wifi")

    # We don't want to bombard the MQTT server!
    print("Waiting...")
    utime.sleep(20)
