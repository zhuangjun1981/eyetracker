# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 22:02:37 2013

@author: derricw
#------------------------------------------------------------------------------ 
EyeTracker.py
#------------------------------------------------------------------------------ 

Dependencies:
SimpleCV http://simplecv.org/
Numpy
Matplotlib

"""

from SimpleCV import *
from pylab import *
import time
import platform
import numpy as np
import math
import cv2

def dist2d(p1,p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 +
                     (p2[1] - p1[1]) ** 2) 

def dist3d(p1,p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 +
                     (p2[1] - p1[1]) ** 2 +
                     (p2[2] - p1[2]) ** 2) 

class Eyetracker(object):
    def __init__(self):
        """Docstring for Eyetracker"""
        self._framecount = 0

        self.camproperties = {
            'hue':248140158.0,
            'saturation': 83.0,
            'brightness': 100.0, 
            'height': 480, 
            'width': 640, 
            'gain': 248140158.0, 
            'contrast': 10.0, 
            'exposure': -6.0    
        }

        self.blur = 0
        self.zoom = 0
        self.ledthresh = 253
        self.pupilthresh = 221
        self.ledsize = [10,1400]
        self.ledarea = 4
        self.pupilarea = 4
        self.pupilsize = [200,10000]

        self.showTriangle = True
        self.printOutput = False
        self.recording = False
        
        self.displayMode = 0
        self.showProcessing = True

        self.led_roi = None #hack, think of a better way

        #locations
        self.pupil = [-1,-1]
        self.led = [-1,-1]
        
        #locations moving average
        self.pupilx = [0,0,0,0,0]
        self.pupily = [0,0,0,0,0]
        self.ledx = [0,0,0,0,0]
        self.ledy = [0,0,0,0,0]

        #get cam
        self.getNewCam()

        if (platform.system()=="Linux"):
            print "Running on Linux, can't change cam properties..."
        else:
            try:
                for p in self.camproperties.keys():
                    if p in self.cam.prop_map:
                        self.setCamProp(p)
            except:
                print "Couldn't set initial camera properties"

        #self._disp = Display()
        cv2.namedWindow("Live")

        self._tick = time.clock()
        self._tock = time.clock()

        #get image size
        f0 = self.cam.getImage() #get size of image camera is putting out
        self.width,self.height = f0.width,f0.height #initialize image size
        self.maxsize = (self.width,self.height) #get max size

        #ROI
        self.roi = None
        self.up,self.dwn = None,None

        #create a gaze tracker instance
        self.gt = GazeTracker()


    def getNewCam(self):
        #self.cam = Camera(prop_set=self.camproperties) #actual camera
        #print self.cam.getAllProperties()
        #self.cam = VirtualCamera(r"res/mouseeye.png",'image') #virtual camera uses image of mouse eye
        self.cam = VirtualCamera(r"C:\Users\derricw\Videos\127146_140125_windowmix_eye.avi",'video')

    def startVideo(self,path):
        self.vs=VideoStream(path,30,False)
        self.vs.fourcc=cv.CV_FOURCC(*'XVID')
        self.recording = True

    def stopVideo(self):
        self.vs=None
        self.recording = False

    def setCamProp(self,prop):
        """Sets a camera property"""
        cv.SetCaptureProperty(self.cam.capture,
            self.cam.prop_map[prop], self.camproperties[prop])

    def getAllData(self):
        return (self.led,self.pupil,self.pupilarea,time.clock())

    def getGaze(self):
        """Returns the monitor pixel of the gaze
            (0,0) is center of screen
        """
        x,y = self.led[0]-self.pupil[0],self.led[1]-self.pupil[1] #get triangle sides
        print "Pixel Distance:",x,y
        theta,phi = self.gt.getAngles(x,y)
        print "Theta Phi:",theta,phi
        dx,dy = self.gt.getGaze(theta,phi)
        print "Dx Dy:",dx,dy
        #something wrong with this now, not sure what
        #print x, y
        return dx,dy

    def nextFrame(self):
        """GETS NEXT FRAME AND PROCESSES IT"""
        ##TODO: SPLIT THIS UP.  SHOULD BE SEVERAL COMPARTMENTALIZED FUNCTIONS
        #if self._disp.isNotDone():
        original = self.cam.getImage() #get camera image

        #GREYSCALE
        i = original.grayscale()

        #ROI?
        if self.roi is not None:
            i = i.regionSelect(*self.roi)
            if self.showProcessing == False:
                original = original.regionSelect(*self.roi)

        #ZOOM?
        if self.zoom is not 0:
            i = i.regionSelect(int(self.width/100*self.zoom),int(self.height/100*self.zoom),
                int(self.width-self.width/100*self.zoom),int(self.height-self.height/100*self.zoom))

        #BLUR?
        if self.blur is not 0:
            i = i.blur(window=(self.blur,self.blur))

        #EQUALIZE
        i = i.equalize()

        #FIND LED
        if self._framecount%10==0:
            self._framecount=0    
            self.binaryLED = i.binarize(thresh=self.ledthresh).invert() #get LED
            led = i.findBlobsFromMask(self.binaryLED,minsize=self.ledsize[0],
                maxsize=self.ledsize[1])
            if led:
                if(len(led)>0): # if we got a blob
                    new = [led[-1].x,led[-1].y]
                    #print led[-1].isCircle(tolerance=0.25)
                    if self.led_roi is None:                           
                        self.led = new
                        self.ledarea = led[-1].area()
                    else:
                        if self.led_roi[0]<new[0]<self.led_roi[2] and \
                            self.led_roi[1]<new[1]<self.led_roi[3]:
                            self.led=new
                            self.ledarea = led[-1].area()
        
        #FIND PUPIL
        self.binaryPupil = i.invert().binarize(thresh=self.pupilthresh).invert()
        self.binaryPupil = self.binaryPupil.morphClose().morphClose().morphClose().morphClose()
        pupil = i.findBlobsFromMask(self.binaryPupil,minsize=self.pupilsize[0],
            maxsize=self.pupilsize[1])
        if pupil:
            if(len(pupil)>0): # if we got a blob
                #print pupil[-1].isCircle(tolerance=0.3)
                self.pupilx.pop(0);self.pupily.pop(0)
                self.pupilx.append(pupil[-1].x)
                self.pupily.append(pupil[-1].y)
                self.pupil = [int(np.mean(self.pupilx)),int(np.mean(self.pupily))]
                self.pupilarea = pupil[-1].area()

        if self.showProcessing:
            todraw = i
        else:
            todraw = original
            
        #DRAW TRIANGLE?
        if self.showTriangle:
            todraw.drawLine(self.led,(self.pupil[0],self.led[1]),color=Color.ORANGE,thickness=1)
            todraw.drawLine((self.pupil[0],self.led[1]),self.pupil,color=Color.BLUE,thickness=1)
            todraw.drawCircle(self.led,max(int(np.sqrt(self.ledarea/np.pi)),4),color=Color.GREEN,thickness=2)
            todraw.drawCircle(self.pupil,max(int(np.sqrt(self.pupilarea/np.pi)),4),color=Color.RED,thickness=2)

        #DRAW FPS
        try:
            self._tock = int(1/(time.clock()-self._tick))
        except:
            pass
        self._tick = time.clock()
        todraw.drawText(str(self._tock),0,i.height-10)

        #SHOW IMAGE
        try:
            if self.displayMode == 0:
                #todraw.save(self._disp)
                cv2.imshow("Live", todraw.getNumpy())
            elif self.displayMode == 1:
                #self.binaryLED.save(self._disp)
                cv2.imshow("Live", self.binaryLED.getNumpy())
            elif self.displayMode == 2:
                #self.binaryPupil.save(self._disp)
                cv2.imshow("Live", self.binaryPupil.getNumpy())
        except Exception, e:
            print e
            
        cv2.waitKey(1)
            
        #SAVE IMAGE?
        if self.recording:
            todraw.save(original)

        #UPDATE FRAMECOUNT
        self._framecount += 1  

        #HANDLE CLICKS IN DISPLAY
        """
        dwn = self._disp.leftButtonDownPosition()
        up = self._disp.leftButtonUpPosition()
        right = self._disp.rightButtonDownPosition()

        #GET ROI FROM MOUSE CLICKS
        if dwn is not None:
            self.dwn = dwn
        if up is not None:
            self.up = up
        if self.up is not None and self.dwn is not None:
            if self.roi is None:
                self.roi = (min(self.dwn[0],self.up[0]),min(self.dwn[1],self.up[1]),
                    max(self.up[0],self.dwn[0]),max(self.up[1],self.dwn[1]))
                self.width,self.height = self.roi[2]-self.roi[0], self.roi[3]-self.roi[1]
            else:
                self.led_roi = (min(self.dwn[0],self.up[0]),min(self.dwn[1],self.up[1]),
                    max(self.up[0],self.dwn[0]),max(self.up[1],self.dwn[1]))
                print "New led ROI: ",self.led_roi
            self.dwn,self.up=None,None
        if right is not None:
            self.dwn,self.up,self.roi,self.led_roi=None,None,None,None
            (self.width,self.height)=self.maxsize
        """



    def close(self):
        #self._disp.quit()
        cv2.destroyAllWindows()

class GazeTracker(object):
    """docstring for GazeTracker"""
    ##TODO: READ MONITOR INFO FROM CONFIG FILE
    def __init__(self):
        self.monitorsize=(49,25)
        self.monitorresolution=(1920,1080)
        self.monitordistance=15 #distance of mouse relative to screen
        self.mousex=self.monitorsize[0]/2 #x position of mouse relative to screen
        self.mousey=self.monitorsize[1]/2 #y position of mouse relative to screen
        self.leddistance=32.0 #distance of LED from mouse FLOAT #should be calculated...
        self.ledx=0.0 #x position of LED relative to mouse FLOAT
        self.ledy=12.0 #y position of LED relative to mouse FLOAT
        self.imgw=640
        self.imgh=480
        self.camfov=3.01 #IN CM, at mouse distance measured manually
        self.eyeradius=0.33 #average for adult mouse

    ##TODO: REWRITE THIS WHOLE THING.... Wrong but close enough for now
    def getAngles(self,x,y):
        theta = np.arcsin(1.0*x*self.camfov/800/self.eyeradius)
        phi = np.arcsin(1.0*y*self.camfov/800/self.eyeradius)
        return theta,phi

    def getGaze(self,theta,phi):
        alpha = self._getAlpha()
        x = np.radians(theta+0)
        y = np.radians(phi+alpha)
        return x,y
        
    def _getAlpha(self):
        alpha = np.arctan(self.ledy/self.monitordistance)
        return alpha
        
    

def main():
    pass

if __name__ == '__main__':
    main()