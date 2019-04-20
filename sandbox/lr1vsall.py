#!/usr/bin/env python

import scipy.io as sio
import cv2
import numpy as np
import random as rnd
import os

imgW=20
imgH=20

nbImages=5000

print(os.getcwd())
pattern = sio.loadmat('ex3data1.mat')
img=pattern['X']    # A numpy array 
label=pattern['y'][:,0]   # A numpy array

weights = sio.loadmat('lR_weights.mat')   
theta=weights['all_theta']      # A numpy array


nbImages1Row=10
nbImages1Col=10
img100=np.zeros((imgH*nbImages1Col, imgW*nbImages1Row))

for i in range(10):
  for j in range(10):
    tmp=np.reshape(img[(rnd.randint(0,5000)),:], (20,20))
    tmp=np.transpose(tmp)
    img100[i*imgH:i*imgH+20,j*imgW:j*imgW+20]=tmp

cv2.imwrite("img100.tif",img100)

# Insert column of 1's for the input data for prediction / LR calculation
imgRev=np.insert(img,0,1,axis=1)

thetaTp=np.transpose(theta)
resY=np.matmul(imgRev,thetaTp)
prediction=np.argmax(resY,axis=1) + 1 # +1 to correct indexing due to speciality of the example. See docs ex3.pdf 
 
nb_correct=0
#print(label,label.shape,prediction,prediction.shape,nb_correct)
for i in range(len(prediction)):
  if(label[i] == prediction[i]):
    nb_correct+=1
tAcc=(100.0*nb_correct)/(len(prediction))   
print("Predicted examples: {:d}".format(len(prediction)))
print("Expected Training Accuracy: 94.90% Measured: {:0.2f}% approx".format(tAcc))


