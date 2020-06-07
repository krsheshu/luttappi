#!/usr/bin/env python

import scipy.io as sio
import cv2
import numpy as np
import random as rnd
import math
import os


class LogisticRegression1vsAllModel():
    '''
    A Python Model for Logistic Regression 1 vs all
    as given in Coursera example ex3

    Args:
        Nil

    Attributes:
        imgW      (int): Image width
        imgH      (int): Image Height
        nbImages  (int): number of Images in the example
    '''

    def __init__(self):

        self.imgW       = 20
        self.imgH       = 20
        self.nbImages   = 5000

    def samplesArray_get(self, rowNb, img, labelY):

        '''
        Returns the samples Array

        Args:
            rowNb         (int): list of randomly selected row numbers
            img   (numpy array): example numpy array
            labelY        (int): reference y label input

        Raises:
            Nil

        Returns:
            sampleImgArray: Required number of images in an array with offset of 1 included
            sampleLabel:  Corresponding labels for the respective classify images
        '''

        nbClassifyImages=len(rowNb)

        sampleImgArray=np.zeros((nbClassifyImages,self.imgW*self.imgH))
        sampleLabel=np.zeros(nbClassifyImages)

        for i in range(nbClassifyImages):

          sampleImgArray[i,:]=img[rowNb[i],:]
          sampleLabel[i]= 0 if labelY[rowNb[i]] == 10 else labelY[rowNb[i]]

        # Insert column of 1's for the input data for prediction / LR calculation
        sampleImgArray=np.insert(sampleImgArray,0,1,axis=1)     # Selected array to return to the user

        return sampleImgArray, sampleLabel



    def nbArray2Image_convert(self, numberArray, nbImages1Col, nbImages1Row,  filename="modelPrediction.tif"):

        '''
        Returns an image array comprising of the input numbers.

        Args:
            numberArray   (numpy array):  A 1D array of numbers to be converted to an image
            nbImages1Col          (int):  expected number of images in one column
            nbImages1Row          (int):  expected number of images in one row
            filename              (str):  File to be saved to

        Raises:
            Nil

        Returns:
            fullImgArray  (numpy array):  The resulting image manufactured from the input number array
        '''

        # Single image size
        imgH=imgW=64
        fullImgArray = np.zeros((imgH*nbImages1Col,imgW*nbImages1Row), np.uint8)
        font = cv2.FONT_HERSHEY_SIMPLEX
        k=0
        for i in range(nbImages1Col):
          for j in range(nbImages1Row):
            img = np.zeros((imgH,imgW), np.uint8)
            nbStr= str(numberArray[k])
            cv2.putText(img,nbStr,(imgW>>2,imgH>>1), font, 1,(255,255,255),2,cv2.LINE_AA)
            k += 1
            fullImgArray[i*imgH:i*imgH+imgH,j*imgW:j*imgW+imgW]=img

        cv2.imwrite(filename,fullImgArray)

        return fullImgArray


    def get(self,nbClassifyImages=10, display=False):

        '''
        Returns nbClassifyImages number of images and the corresponding labels
        from the image example code from Coursera ex3.
        Saves also a testImages.tif with these randomly selected images

        Args:
            nbClassifyImages (int): The number of images to be returned randomly from the imager Array

        Raises:
            AssertionError: If nbClassifyImages not power of 2

        Returns:
            sampleImgArray(numpy array):  nbClassifyImages number of images in an array with offset of 1 included
            sampleLabel   (numpy array):  Corresponding labels for the respective classify images
            theta         (numpy array):  Learned Weights for the logistic regression calculation
            modelPredict  (numpy array):  Prediction results for the samples by the model
        '''

        assert (math.sqrt(nbClassifyImages)%1 == 0),"ERR016: nb Classify images not power of 2!"

        origDir=os.getcwd()
        os.chdir(os.path.dirname(__file__))

        pattern = sio.loadmat('ex3data1.mat')
        img=pattern['X']          # A numpy array
        labelY=pattern['y'][:,0]   # A numpy array

        weights = sio.loadmat('lR_weights.mat')
        theta=weights['all_theta']      # A numpy array

        nbImages1Row=int(math.sqrt(nbClassifyImages))
        nbImages1Col=int(math.sqrt(nbClassifyImages))

        testImgs=np.zeros((self.imgH*nbImages1Col, self.imgW*nbImages1Row))

        rowNb=[]
        for i in range(nbClassifyImages):
          rowNb.append(rnd.randint(0,self.nbImages-1))

        for i in range(nbImages1Col):
          for j in range(nbImages1Row):
            tmp=np.reshape(img[rowNb[i*nbImages1Row+j],:], (20,20))
            tmp=np.transpose(tmp)
            testImgs[i*self.imgH:i*self.imgH+self.imgH,j*self.imgW:j*self.imgW+self.imgW]=tmp

        sampleImgName="sampleImages.tif"
        cv2.imwrite(sampleImgName,testImgs)
        print("Test image saved as {}".format(sampleImgName))

        sampleImgArray, sampleLabel = self.samplesArray_get(rowNb, img, labelY)

        imgRev=np.insert(img,0,1,axis=1)            # Array for prediction calculation

        thetaTp=np.transpose(theta)
        resY=np.matmul(imgRev,thetaTp)
        prediction=np.argmax(resY,axis=1) + 1 # +1 to correct indexing due to speciality of the example. See docs ex3.pdf

        modelPredict=np.zeros(nbClassifyImages,np.uint8)
        for i in range(nbClassifyImages):
          modelPredict[i] = 0 if prediction[rowNb[i]] == 10 else int(prediction[rowNb[i]])

        predictImgName="modelPrediction.tif"
        predictFullImg=self.nbArray2Image_convert(modelPredict,nbImages1Col, nbImages1Row, predictImgName)
        print("Prediction image saved as {}".format(predictImgName))

        nb_correct=0
        #print(label,label.shape,prediction,prediction.shape,nb_correct)
        for i in range(len(prediction)):
          if(labelY[i] == prediction[i]):
            nb_correct+=1
        tAcc=(100.0*nb_correct)/(len(prediction))
        print("Predicted examples: {:d}".format(len(prediction)))
        print("Expected Training Accuracy: 94.90% Measured: {:0.2f}% approx".format(tAcc))

        os.chdir(origDir)

        if display==True:
            cv2.imshow(sampleImgName,testImgs)
            cv2.imshow(predictImgName,predictFullImg)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return sampleImgArray, sampleLabel, theta, modelPredict

if __name__ == "__main__":
    model=LogisticRegression1vsAllModel()
    sampleImgArray, sampleLabel, theta, modelPredict = model.get(nbClassifyImages=100,display=True)
    #sampleImgArray, sampleLabel, theta, modelPredict = model.get(nbClassifyImages=100)
    #print(sampleImgArray, sampleLabel)
