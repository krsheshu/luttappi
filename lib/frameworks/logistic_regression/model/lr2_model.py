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
            imgArray: Required number of images in an array with offset of 1 included
            label:  Corresponding labels for the respective classify images  
        '''

        nbClassifyImages=len(rowNb)
 
        imgArray=np.zeros((nbClassifyImages,self.imgW*self.imgH))
        label=np.zeros(nbClassifyImages)

        for i in range(nbClassifyImages):

          imgArray[i,:]=img[rowNb[i],:]     
          label[i]= labelY[rowNb[i]]  
        
        # Insert column of 1's for the input data for prediction / LR calculation
        imgArray=np.insert(imgArray,0,1,axis=1)     # Selected array to return to the user
        
        return imgArray, label


    def get(self,nbClassifyImages=10):

        '''
        Returns nbClassifyImages number of images and the corresponding labels 
        from the image example code from Coursera ex3.
        Saves also a testImages.tif with these randomly selected images 

        Args:
            nbClassifyImages (int): The number of images to be returned randomly from the imager Array

        Raises:
            AssertionError: If nbClassifyImages not power of 2 

        Returns:
            imgArray: nbClassifyImages number of images in an array with offset of 1 included
            label:  Corresponding labels for the respective classify images  
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
         
        imageName="testImages.tif"
        cv2.imwrite(imageName,testImgs)
        print("Test image saved as {}".format(imageName))
       
        imgArray, label = self.samplesArray_get(rowNb, img, labelY) 

        imgRev=np.insert(img,0,1,axis=1)            # Array for prediction calculation
        
        thetaTp=np.transpose(theta)
        resY=np.matmul(imgRev,thetaTp)
        prediction=np.argmax(resY,axis=1) + 1 # +1 to correct indexing due to speciality of the example. See docs ex3.pdf 
        
        nb_correct=0
        #print(label,label.shape,prediction,prediction.shape,nb_correct)
        for i in range(len(prediction)):
          if(labelY[i] == prediction[i]):
            nb_correct+=1
        tAcc=(100.0*nb_correct)/(len(prediction))   
        print("Predicted examples: {:d}".format(len(prediction)))
        print("Expected Training Accuracy: 94.90% Measured: {:0.2f}% approx".format(tAcc))
        
        os.chdir(origDir)
       
        return imgArray, label 

if __name__ == "__main__": 
    model=LogisticRegression1vsAllModel()
    imgArray,label = model.get(16)
    #print(imgArray, label)
