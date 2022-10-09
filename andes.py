from ctypes import sizeof
import json
import os 
import cv2
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv
from paho.mqtt import client as MQTT_Client
import time

load_dotenv()

width = 640
height = 384
line_width = 10
color_depth = 2
three_color = {
    'white': 0b11,
    'red': 0b01,
    'black': 0b00
}

mongodb = MongoClient(
    f'{os.environ.get("SERVER_PROTOCOL")}://{os.environ.get("MONGO_USER")}:{os.environ.get("MONGO_PASSWORD")}@{os.environ.get("SERVER")}')[os.environ.get("DATABASE")]
data = mongodb['Inventory_Data'].find_one({"cabinet": "A"})

client = MQTT_Client.Client()

@client.connect_callback()
def on_connect(client, userdata, flags_dict, reason):
    print(f"========== {'Start Connect':^15s} ==========")
    

@client.disconnect_callback()
def on_disconnect(userdata, result_code):
    print(f"========== {'End Connect':^15s} ==========")


cabinet_width = width // len(data["position"])
cabinet_height = height // len(data["position"][0])
cabinet = list()

for row_index, i in enumerate(data["position"]):
    cabinet_row = list()
    for col_index, j in enumerate(i):
        img = np.zeros((cabinet_height, cabinet_width, 3), np.uint8)
        img.fill(255)
        # (影像, 頂點座標, 對向頂點座標, 顏色, 線條寬度)
        cv2.rectangle(img, (0, 0), (cabinet_width, cabinet_height),
                    (0, 0, 0), line_width)
        # (影像, 文字, 座標, 字型, 大小, 顏色, 線條寬度, 線條種類)
        cv2.putText(img, j,
                    (line_width * 2, cabinet_height // 2 - line_width * 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(img, str(data["num"][j]),
                    (line_width * 2, cabinet_height - line_width * 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2, cv2.LINE_AA)
        cabinet_row.append(img)
    cabinet.append(cv2.hconcat(cabinet_row))
img = cv2.vconcat(cabinet)
print(img.shape)


def convert_three_color(color_value, color_reverse=False, threshold=128):
    if np.dot(color_value, [0.299, 0.587, 0.114]) > threshold:
        return three_color['white']
    elif color_value[0] > threshold:
        return three_color['red']
    else:
        return three_color['black']


image_length = img.shape[0]*img.shape[1]*color_depth//8
convert_img = np.zeros((image_length, ), dtype=np.int32)
for i in range(img.shape[0]):
    for j in range(0, img.shape[1], 8//color_depth):
        temp_val = 0
        for k in range(8//color_depth):
            temp_val |= convert_three_color(
                img[i][j+k])
            temp_val <<= color_depth
        temp_val >>= color_depth
        convert_img[(i*img.shape[1]+j)//4] = temp_val

img_val_list = list()
for img_val in convert_img:
    val = hex(img_val).split('0x')[1].upper()
    if len(val) < 2:
        val = f"0{val}"
    img_val_list.append(f"0X{val}")

# print({"img": len(img_val_list)})

result1 = ",".join(img_val_list[:48])
result2 = ",".join(img_val_list[25000:50000])
result3 = ",".join(img_val_list[50000:])

client.connect("192.168.1.97", 1883, 60)
# print(len(result))
for i in range(0, len(img_val_list), 48):
    print(len(img_val_list))
    print(range(0, len(img_val_list), 48))
    client.publish(f'drawA/{int(i/48)}', ",".join(img_val_list[i:i+48]))
    print(",".join(img_val_list[i:(i+48)]))
    time.sleep(0.01)
    break
# client.publish('draw/A_2', result2)
# time.sleep(1)
# client.publish('draw/A_3', result3)
# time.sleep(1)
client.publish('draw/B', "result")