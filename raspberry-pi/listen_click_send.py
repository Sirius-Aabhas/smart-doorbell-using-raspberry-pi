import paho.mqtt.client as mqtt
from picamera import PiCamera
import requests 

'''	Function to publish the file in bytearray format	'''
def send_image_mqtt(filename):
	with open(filename,'rb') as f:
		fileContent = f.read()
	byteArr = bytearray(fileContent)
	client.publish('iitkgp/iot/doorbell/image', byteArr, 0)
	print("[INFO] File is published to iitkgp/iot/doorbell/image")

'''	Function to publish the file in bytearray format	'''
def send_image_rest(filename):
	with open(filename,'rb') as f:
		fileContent = f.read()
	byteArr = bytearray(fileContent)
	serverUrl = 'http://10.145.248.168:5002/processImage'
	status = requests.post(url = serverUrl, data = byteArr)
	print('[INFO] POST done with ',status)

'''	This function subscribes to required topics on getting connected to broker	'''
def on_connect(client, userdata, flags, rc):
	print("[INFO] Connected with exit code ", str(rc))
	client.subscribe('iitkgp/iot/doorbell/bell')

'''	This function clicks an image and sends it	'''
def on_message(client, userdata, msg):
	print("[INFO] Received message from  '"+msg.topic+"' -- '"+ str(msg.payload)+"'")
	camera.capture('mqClick.png', format='png')
	print("[INFO] Image is clicked")
	send_image_rest('mqClick.png')

#Create a mqtt object 
client = mqtt.Client()
#Create an object for the RPi Camera
camera = PiCamera()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_forever()
