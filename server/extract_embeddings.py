from imutils import paths
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

print("[INFO] loading face recognizer...")
embedder = cv2.dnn.readNetFromTorch('openface_nn4.small2.v1.t7')

print("[INFO] fetching face files...")
imagePaths = list(paths.list_images('dataset'))

# initialize our lists of extracted facial embeddings and people names
knownEmbeddings = []
knownNames = []

# initialize the total number of faces processed
total = 0

for (i, imagePath) in enumerate(imagePaths):
	# extract the person name from the image path
	print("[INFO] processing image {}/{}".format(i + 1,
		len(imagePaths)))
	name = imagePath.split(os.path.sep)[-2]

	# load the image, resize it and grab the image dimensions
	image = cv2.imread(imagePath)
	image = imutils.resize(image, width=600)
	(h, w) = image.shape[:2]

	# construct a blob from the image and localize faces
	imageBlob = cv2.dnn.blobFromImage(
		cv2.resize(image, (300, 300)), 1.0, (300, 300),
		(104.0, 177.0, 123.0), swapRB=False, crop=False)
	detector.setInput(imageBlob)
	detections = detector.forward()

	# proceed if a face was found
	if len(detections) > 0:

		i = np.argmax(detections[0, 0, :, 2])
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
			faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
				(96, 96), (0, 0, 0), swapRB=True, crop=False)
			embedder.setInput(faceBlob)
			embedding = embedder.forward()

			# add the names and embeddings to the lists
			knownNames.append(name)
			knownEmbeddings.append(embedding.flatten())
			total += 1

# save the faces and embedding to a file
print("[INFO] serializing {} encodings...".format(total))
data = {"embeddings": knownEmbeddings, "names": knownNames}
with open('output/embeddings.pickle', "wb") as f:
	f.write(pickle.dumps(data))
