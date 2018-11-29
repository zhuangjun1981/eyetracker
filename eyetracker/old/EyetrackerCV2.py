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
import sys
import ConfigParser
from image_processor import ImageProcessor


def dist2d(p1,p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 +
                     (p2[1] - p1[1]) ** 2) 


def dist3d(p1,p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 +
                     (p2[1] - p1[1]) ** 2 +
                     (p2[2] - p1[2]) ** 2) 


class Eyetracker(object):
    def __init__(self,camera=None,video=None):
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

        self.ip = ImageProcessor()

        #hardcode some defaults (to be overwritten by config file)
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
        self.getCamera(camera,video)

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
        cv2.setMouseCallback("Live",self.on_mouse,0)

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
        
        #GET CONFIG
        config = {}
        try:
            path = r"C:/AibStim/config/eyetracking.cfg"
            if os.path.exists(path):
                localconfig = ConfigParser.RawConfigParser()
                localconfig.read(path)
                for (k,v) in localconfig.items("Eyetracker"):
                    config[k]=eval(v)
            else:
                print "Couldn't find config file.",path
        except Exception, e:
            print "Error reading config file %s: "%(path),e
        for k,v in config.iteritems():
            setattr(self, k, v)


    def getCamera(self,camera=None,video=None):

        if camera == None:
            if video == None:
                self.cam = VirtualCamera(r"res/mouseeye.png",'image') #virtual camera uses image of mouse eye
            else:
                self.cam = VirtualCamera(video,'video')
        elif camera.lower() == "webcam":
            self.cam = Camera(prop_set=self.camproperties) #actual camera
        elif camera.lower() == "avt":
            from toolbox.Cameras.avt import Camera
            self.cam = Camera()
            time.sleep(2)

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

    def getAllData(self):
        return (self.led,self.pupil,self.pupilarea,time.clock())

    def getGaze(self):
        """Returns the monitor pixel of the gaze
            (0,0) is center of screen
        """
        x,y = self.led[0]-self.pupil[0],self.led[1]-self.pupil[1] #get triangle sides
        #print "Pixel Distance:",x,y
        theta,phi = self.gt.getAngles(x,y)
        #print "Theta Phi:",theta,phi
        dx,dy = self.gt.getGaze(theta,phi)
        #print "Dx Dy:",dx,dy
        #something wrong with this now, not sure what
        #print x, y
        return dx,dy,self.pupilarea

    def nextFrame(self, show_video=True):
        """GETS NEXT FRAME AND PROCESSES IT"""
        ##TODO: SPLIT THIS UP.
        original = self.cam.getImage() #get camera image

        #preprocess
        i = self.ip.preprocess(original,self.roi,gray=True,blur=self.blur,
            equalize=True,zoom=self.zoom)

        #find led
        self.binaryLED, led, led_area = self.ip.get_led(i, self.ledsize, 
            self.ledthresh, self.led_roi)

        if led:
            self.led=led
            self.ledarea = led_area
            if self.roi:
                self.led = [self.led[0]+self.roi[0],self.led[1]+self.roi[1]] #add roi for absolute img coords

        self.binaryPupil, pupil, pupil_area = self.ip.get_pupil(i, self.pupilsize, self.pupilthresh)

        if pupil:
            self.pupilx.pop(0);self.pupily.pop(0)
            self.pupilx.append(pupil[0])
            self.pupily.append(pupil[1])
            self.pupil = [int(np.mean(self.pupilx)),int(np.mean(self.pupily))]
            self.pupilarea = pupil_area
            if self.roi:
                self.pupil = [self.pupil[0]+self.roi[0],self.pupil[1]+self.roi[1]]

        if self.displayMode == 0:
            if self.showProcessing:
                todraw = i
            else:
                todraw = original
        elif self.displayMode == 1:
            todraw = self.binaryLED
        elif self.displayMode == 2:
            todraw = self.binaryPupil
            
        todraw = todraw.getNumpyCv2()
        
        if self.showTriangle:
            ledpos = tuple(self.led)
            pupilpos = tuple(self.pupil)   
            if self.showProcessing or (self.displayMode!=0):
                if self.roi:
                    #subtract roi offset if necessary
                    ledpos = tuple([self.led[0]-self.roi[0],self.led[1]-self.roi[1]])
                    pupilpos = tuple([self.pupil[0]-self.roi[0],self.pupil[1]-self.roi[1]])

            #draw everything
            cv2.line(todraw,ledpos,(pupilpos[0],ledpos[1]),color=(0,165,255),thickness=1)
            cv2.line(todraw,(pupilpos[0],ledpos[1]),pupilpos,color=(255,0,0),thickness=1)
            cv2.circle(todraw,tuple(ledpos),max(int(np.sqrt(self.ledarea/np.pi)),4),color=(0,255,0),thickness=2)
            cv2.circle(todraw,tuple(pupilpos),max(int(np.sqrt(self.pupilarea/np.pi)),4),color=(0,0,255),thickness=2)
        
        #DRAW FPS
        try:
            self._tock = int(1./(time.clock()-self._tick))
        except:
            pass
        self._tick = time.clock()

        #SHOW IMAGE
        if show_video:
            cv2.imshow("Live",todraw)
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
            else:
                self.led_roi = (min(self.dwn[0],self.up[0]),min(self.dwn[1],self.up[1]),
                    max(self.up[0],self.dwn[0]),max(self.up[1],self.dwn[1]))
                print"New led ROI: ",self.led_roi
            self.dwn,self.up = None,None


    def run(self, show_video=True):
        data = []
        while 1:
            try:
                self.nextFrame(show_video)
                data.append(self.getAllData())
            except:
                cv2.destroyAllWindows()
                break
        return data



    def close(self):
        cv2.destroyAllWindows()

class GazeTracker(object):
    """docstring for GazeTracker"""

    def __init__(self):
        
        #BUNCH OF DEFAULTS NOT ALL GET USED AT THIS POINT
        self.monitorsize=(51,25)
        self.monitorresolution=(1920,1080)
        self.monitordistance=15 #distance of mouse relative to screen
        self.mousex=self.monitorsize[0]/2 #x position of mouse relative to screen
        self.mousey=self.monitorsize[1]/2 #y position of mouse relative to screen
        self.leddistance=32.0 #distance of LED from mouse FLOAT #should be calculated...
        self.ledx=0.0 #x position of LED relative to mouse FLOAT
        self.ledy=12.0 #y position of LED relative to mouse FLOAT
        self.imgw=640 #should get from video
        self.imgh=480 #should get from video
        self.camfov=1.5 #IN CM, at mouse distance measured manually
        self.eyeradius=0.165 #average for adult mouse (0.33 diameter)

        #GET CONFIG TO OVERWRITE DEFAULTS
        config = {}
        try:
            path = r"C:/AibStim/config/eyetracking.cfg"
            if os.path.exists(path):
                localconfig = ConfigParser.RawConfigParser()
                localconfig.read(path)
                for (k,v) in localconfig.items("Gazetracker"):
                    config[k]=eval(v)
            else:
                print "Couldn't find config file.",path
        except Exception, e:
            print "Error reading config file %s: "%(path),e
        for k,v in config.iteritems():
            setattr(self, k, v)

    def getAngles(self,x,y):
        ##TODO: Wrong but close enough to test
        theta = np.arcsin(1.0*x*self.camfov/np.sqrt(self.imgw**2+self.imgh**2)/self.eyeradius)
        phi = np.arcsin(1.0*y*self.camfov/np.sqrt(self.imgw**2+self.imgh**2)/self.eyeradius) 
        return theta,phi

    def getGaze(self,theta,phi):
        alphax,alphay = self._getAlpha()
        x = np.rad2deg(theta+alphax)
        y = np.rad2deg(phi+alphay)
        return x,y
        
    def _getAlpha(self):
        alphay = np.arctan(self.ledy/self.monitordistance)
        alphax = np.arctan(self.ledx/self.monitordistance)
        return alphax,alphay

        
def positions2gaze(led_locations,pupil_locations):
    gt = GazeTracker()
    delta = led_locations-pupil_locations
    deltax = delta[:,0]
    deltay = delta[:,1]
    azi,zen = gt.getAngles(deltax,deltay)
    azi,zen = gt.getGaze(azi,zen) #adjust for camera off-centeredness, convert to degrees
    return azi,zen
    

if __name__ == '__main__':

    print sys.argv
    #path = sys.argv[1]
    path = r"\\aibsdata\neuralcoding\Behavior\2014.05.20_M123638_EyeTracking\140520135358-foraging-mouseTEST-DougO-1.avi"
    et = Eyetracker(video=path)
    et.showProcessing = False
    data = et.run(True)
    roi = et.roi
    led_location = np.array([d[0] for d in data])
    pupil_location = np.array([d[1] for d in data])
    pupil_area = np.array([d[2] for d in data])
    times = np.array([d[3] for d in data])
    
    azi,zen = positions2gaze(led_location, pupil_location) # in degrees on screen (ideally)
    
    
    