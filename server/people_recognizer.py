import numpy as np
import imutils
import pickle
import cv2
import os

print("[INFO] loading face detector...")
protoPath = os.path.sep.join(['face_detection_model', 'deploy.prototxt'])
modelPath = os.path.sep.join(['face_detection_model',
	'res10_300x300_ssd_iter_140000.caffemodel'])
detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)

print("[INFO] loading face embedder...")
embedder = cv2.dnn.readNetFromTorch('openface_nn4.small2.v1.t7')

print("[INFO] loading face recognizer...")
recognizer = pickle.loads(open('output/recognizer.pickle', 'rb').read())

print("[INFO] loading label encoder...")
le = pickle.loads(open('output/le.pickle', 'rb').read())

''' This function processes the 'imageFile' received to find the faces in it, 
	creates bounds on the faces and returns the tagged image	'''
def recognize_person(imageFile):
	# load the image, resize it, and then grab the image dimensions
	image = cv2.imread(imageFile)
	image = imutils.resize(image, width=600)
	(h, w) = image.shape[:2]

	# construct a blob from the image and localize faces
	imageBlob = cv2.dnn.blobFromImage(
		cv2.resize(image, (300, 300)), 1.0, (300, 300),
		(104.0, 177.0, 123.0), swapRB=False, crop=False)
	detector.setInput(imageBlob)
	detections = detector.forward()

	people=[]

	for i in range(0, detections.shape[2]):
		# extract the confidence value associated with the prediction
		confidence = detections[0, 0, i, 2]

		# filter out weak detections
		if confidence > 0.5:
			# compute the bounding box for the face & extract ROI
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")

			face = image[startY:endY, startX:endX]
			
			# filter out too small faces
			(fH, fW) = face.shape[:2]
			if fW < 20 or fH < 20:
				continue

			# construct a blob from face and calculate the 128-d embeddings
			faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96),
				(0, 0, 0), swapRB=True, crop=False)
			embedder.setInput(faceBlob)
			vec = embedder.forward()

			# perform classification to recognize the face
			preds = recognizer.predict_proba(vec)[0]
			j = np.argmax(preds)
			proba = preds[j]
			name = le.classes_[j]
			people.append(name)

			# draw the bounding box and probability for display
			text = "{}: {:.2f}%".format(name, proba * 100)
			y = startY - 10 if startY - 10 > 10 else startY + 10
			cv2.rectangle(image, (startX, startY), (endX, endY),
				(0, 0, 255), 2)
			cv2.putText(image, text, (startX, y),
				cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

	# show the output image
	#cv2.imshow('Image', image)
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()
	if people:
		# save the tagged image with boxes and return as bytearray
		cv2.imwrite('processed_image.jpg',image)
		with open('processed_image.jpg','rb') as f:
			fileContent = f.read()
		byteArr = bytearray(fileContent)
		return people, byteArr
	return None, None