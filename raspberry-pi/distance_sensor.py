import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time

#set GPIO Mode BCM
GPIO.setmode(GPIO.BCM)

#set GPIO Pins for IN/OUT
GPIO_TRIGGER = 18
GPIO_ECHO = 24
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2

    return distance

if __name__ == '__main__':
	#connect to the broker
	client = mqtt.Client()
	client.connect("localhost", 1883, 60)
	print('[INFO] Connected to broker ',client)
	GPIO.output(GPIO_TRIGGER, False)
	try:
		while True:
			GPIO.output(GPIO_TRIGGER, False)
			dist = distance()
			print ("[DEBUG] Measured Distance = %.1f cm" % dist)
			if dist < 70:
				client.publish('iitkgp/iot/doorbell/bell','From distance sensor', 0)
				print("[INFO] Published message to iitkgp/iot/doorbell/bell ")
			time.sleep(2)
		client.loop_forever()
	finally:
		GPIO.cleanup()
