# -*- coding: utf8 -*-
import json
import time

from paho.mqtt import client as MQTT_Client


# Init connect
client = MQTT_Client.Client()


# Set connect info
client.connect("192.168.1.97", 1883, 60)


# data = [False for i in range(8)]
# data[0] = True

while True:
    # client.publish("mqtt/test", json.dumps({
    #     "Temperature": random.random() * 10 + 20,
    #     "Time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    # }))
    client.publish("hello", "world")
    print("hello", "world")
    time.sleep(10)
