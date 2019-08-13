'''
	This file creates a ReST API server for accepting the images
	and processing them		
'''
from flask import Flask, request
from flask_mqtt import Mqtt
from people_recognizer import recognize_person
import time, os, fnmatch, shutil

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = '10.145.140.20'
app.config['MQTT_BROKER_PORT'] = 1883
client = Mqtt(app)

@app.route('/')
def api_root():
    return 'This is the root of the image processing api'

@app.route('/processImage', methods = ['GET', 'POST'])
def api_images():
    if request.method == 'GET':
        return 'GET method of processImage. Dummy response. Will be implemented in future.'
    elif request.method == 'POST':
        t = time.localtime()
        timestamp = time.strftime('%b-%d-%Y_%H%M%s', t)
        image_name = ('images/image-' + timestamp + '.png')
        with open(image_name,'wb') as f:
            f.write(request.data)
            print('[INFO] Image received and saved')
        #recognize the people in it
        people, processed_image = recognize_person(image_name)

        #If a person is found, publish it
        if people:
            print('[INFO] People in the image are : ',people)
            client.publish('iitkgp/iot/doorbell/processed', processed_image, 0)
            print('[INFO] Image published')
        return 'ECHO: POST\n'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5002', use_reloader=False)
