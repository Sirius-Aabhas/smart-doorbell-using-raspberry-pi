import RPi.GPIO as io
import paho.mqtt.client as mqtt
import time


client = mqtt.Client()
client.connect("localhost", 1883, 60)

print('[INFO] Connected to ',client)

io.setwarnings(False)
#set GPIO Mode BCM
io.setmode(io.BCM)

#set GPIO pin for IN
io.setup(23, io.IN, pull_up_down=io.PUD_DOWN)

while True:
	if io.input(23) == io.HIGH:
		print('[DEBUG] Button pressed')
		client.publish('iitkgp/iot/doorbell/bell','From button', 0)
		print("[INFO] Published message to iitkgp/iot/doorbell/bell")
		time.sleep(0.5)

client.loop_forever()

