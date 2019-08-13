from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import pickle

print("[INFO] loading face embeddings...")
data = pickle.loads(open('output/embeddings.pickle', 'rb').read())

print("[INFO] encoding labels...")
le = LabelEncoder()
labels = le.fit_transform(data['names'])

# train the model used to accept the 128-d embeddings of the face
print("[INFO] training model...")
recognizer = SVC(C=1.0, kernel='linear', probability=True)
recognizer.fit(data['embeddings'], labels)

# save the face recognition model
with open('output/recognizer.pickle', 'wb') as f:
	f.write(pickle.dumps(recognizer))

# savethe label encoder
with open('output/le.pickle', 'wb') as f:
	f.write(pickle.dumps(le))