# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 22:02:37 2013

@author: derricw
#------------------------------------------------------------------------------ 
webcam.py
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
import cv2


class Webcam(object):
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


        self.recording = False

        #get cam
        self.getCamera()

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
        cv2.namedWindow("Webcam")
        cv2.setMouseCallback("Webcam",self.on_mouse,0)

        self._tick = time.clock()
        self._tock = time.clock()

        #get image size
        f0 = self.cam.getImage() #get size of image camera is putting out
        self.width,self.height = f0.width,f0.height #initialize image size
        self.maxsize = (self.width,self.height) #get max size

        #ROI
        self.roi = None
        self.up,self.dwn = None,None


    def getCamera(self):
        self.cam = Camera(prop_set=self.camproperties) #actual camera


    def startVideo(self,path):
        self.vs=VideoStream(path,30,True)
        self.vs.fourcc=cv.CV_FOURCC(*'XVID')
        self.recording = True

    def stopVideo(self):
        self.vs=None
        self.recording = False

    def setCamProp(self,prop):
        """Sets a camera property"""
        cv.SetCaptureProperty(self.cam.capture,
            self.cam.prop_map[prop], self.camproperties[prop])

    def nextFrame(self):
        """GETS NEXT FRAME AND PROCESSES IT"""
        ##TODO: SPLIT THIS UP.  SHOULD BE SEVERAL COMPARTMENTALIZED FUNCTIONS
        original = self.cam.getImage() #get camera image

        #ROI?
        if self.roi is not None:
            todraw = original.regionSelect(*self.roi)
        else:
            todraw = original

        todraw = todraw.getNumpyCv2()

        #SHOW IMAGE
        cv2.imshow("Webcam",todraw)
        cv2.waitKey(1) #ms
            
        #SAVE IMAGE?
        if self.recording:
            original.save(self.vs)

        #UPDATE FRAMECOUNT
        self._framecount += 1  

    def on_mouse(self,event,x,y,flags,params):
        """ Handle clicks in display window. """
        if event == cv2.cv.CV_EVENT_LBUTTONDOWN:
            self.dwn = (x,y)
        elif event == cv2.cv.CV_EVENT_LBUTTONUP:
            self.up = (x,y)
        elif event == cv2.cv.CV_EVENT_RBUTTONDOWN:
            self.dwn,self.up,self.roi,self.led_roi = None,None,None,None
            (self.width,self.height)=self.maxsize
        if self.up is not None and self.dwn is not None:
            if self.roi is None:
                self.roi = (min(self.dwn[0],self.up[0]),min(self.dwn[1],self.up[1]),
                            max(self.up[0],self.dwn[0]),max(self.up[1],self.dwn[1]))
                self.width,self.height = self.roi[2]-self.roi[0],self.roi[3]-self.roi[1]
            self.dwn,self.up = None,None


    def close(self):
        cv2.destroyAllWindows()


def main():
    pass

if __name__ == '__main__':
    main()