# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 17:02:25 2013

@author: derricw

edited by Jun
"""

import numpy as np
import cv2
import socket
import datetime
import time
import os
import sys
import atexit
from toolbox.Cameras.avt import Camera
import shutil

class WebcamRecorder():

    def __init__(self,
                 saveFolder = "C:/AibStim/eyetracking",
                 backupFolder =  None):
        try:
            os.mkdir(saveFolder)
        except WindowsError:
            pass
               
        if backupFolder:
            try:
                os.mkdir(backupFolder)
            except WindowsError:
                pass
            
        self.saveFolder = saveFolder
        self.backupFolder = backupFolder
        self.outputFileName = None
        
        self.propertymap = {
            'width':3,
            'height':4,
            'brightness':10,
            'contrast':11,
            'saturation':12,
        }
        
    
    def run(self, 
        cameras=2, 
        size=(640,480), 
        exposure=-6, 
        brightness=100,
        contrast=5,
        saturation=82,
        ):
        
        #Set up IP to listen for connection...
        IP = '0.0.0.0'
        PORT = 10000

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((IP,PORT))
        self.sock.settimeout(0.0)

        self.cap = [cv2.VideoCapture(i) for i in range(cameras)]
        
        
        self.windows = [cv2.namedWindow(str(i)) for i in range(cameras)]
        

        try:        
            self.avt = Camera()
            self.avt_window = cv2.namedWindow("AVT")
        except Exception, e:
            self.avt = None
            print "Error loading AVT camera:",e

        
        for camera in self.cap:
            camera.set(self.propertymap['width'],size[0])
            camera.set(self.propertymap['height'],size[1])
            camera.set(self.propertymap['brightness'],brightness)
            camera.set(self.propertymap['contrast'],contrast)
            camera.set(self.propertymap['saturation'],saturation)
            time.sleep(3)
        
        run = True
        while run:

            #Try to get two cameras...
            print "Starting %i cameras..."%cameras

            # Define the codec and create VideoWriter object
            fourcc = cv2.cv.CV_FOURCC(*'MPEG')

            print "Waiting on record signal..."
            tick = time.clock()
            while (self.cap[0].isOpened()):
                t = time.clock()
                tock,tick = t-tick,t
                images = [img.read() for img in self.cap]
                

                if self.avt:
                    try:
                        avt_img = self.avt.getImage(100)
                        cv2.imshow("AVT",avt_img)
                    except:
                        pass

                
                for i,img in enumerate(images):
                    if img[0]:
                        frame = img[1]
                        cv2.circle(frame, (20,20), 10, (0,255,0), -1)
                        cv2.imshow(str(i), frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    run=False
                    break
                try:
                    data, addr = self.sock.recvfrom(1024)
                    if data[0]=="1":
                        if len(data) > 1:
                            self.outputFileName = data[1:]
                        else:
                            dt = datetime.datetime.now() 
                            self.outputFileName = dt.strftime('%y%m%d%H%M%S')
                        break
                except:
                    pass
            
            if run:
                start = time.clock()
                print "Starting recording at: ", str(datetime.datetime.now())                    

                self.out = [cv2.VideoWriter(os.path.join(self.saveFolder,self.outputFileName)+"-%i.avi"%i,fourcc, 30.0, size) for i,c in enumerate(self.cap)]
                self.frameoutput = [open(os.path.join(self.saveFolder,self.outputFileName)+"-%i.txt"%i,'w') for i,c in enumerate(self.cap)]


                if self.avt:
                    self.avt_out = cv2.VideoWriter(os.path.join(self.saveFolder,self.outputFileName)+"-avt.avi",fourcc, 30.0, size)
                    self.avt_frameoutput = open(os.path.join(self.saveFolder,self.outputFileName)+"-avt.txt","w")


                while(self.cap[0].isOpened()):
                    
                    images = [img.read() for img in self.cap]
                    t = time.clock()
                    tock,tick = t-tick,t               
                    

                    if self.avt:
                        try:
                            avt_img = self.avt.getImage(100)
                            cv2.imshow("AVT",avt_img)
                            t = time.clock()
                            self.avt_out.write(avt_img)
                            self.avt_frameoutput.write(str(t)+"\n")
                        except:
                            pass

                    
                    for i,img in enumerate(images):
                        if img[0]==True:
                            
                            frame = img[1]
                            self.out[i].write(frame)
                    
                            t=time.clock()
                            self.frameoutput[i].write(str(t)+"\n")
                                
                            cv2.circle(frame, (20,20), 10, (0,0,255), -1)
                            cv2.imshow(str(i),frame)
                        
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        run=False
                        break

                    try:
                        data, addr = self.sock.recvfrom(1024)
                        if data[0] == "0":
                            break
                    except Exception, e:
                        pass
                    
                for out in self.out:
                    out.release()
                    print "Videowriter released..."

                    
                for f in self.frameoutput:
                    f.close()
                    print "Frame interval output closed..."
                    
                if self.avt:
                    self.avt_out.release()
                    print "AVT videowriter released..."
                    self.avt_frameoutput.close()
                    print "AVT camera writer released ..."
                    
                if self.backupFolder:
                    # Check if backup folder exists, if not creat one
                    if not os.path.exists(os.path.dirname(self.backupFolder)):
                        os.mackdirs(os.path.dirname(self.backupFolder))

                    for i,c in enumerate(self.cap):
                        print "backing up movie file ..."
                        shutil.copy2(os.path.join(self.saveFolder,self.outputFileName)+"-%i.avi"%i, self.backupFolder)
                        print "Movie file successfully backed up. \nBacking up frame interval file ..."
                        shutil.copy2(os.path.join(self.saveFolder,self.outputFileName)+"-%i.txt"%i, self.backupFolder)
                        print "Frame interval file successfully backed up. \n\n"
                        
                    if self.avt:
                        print "backing up AVT movie file ..."
                        shutil.copy2(os.path.join(self.saveFolder,self.outputFileName)+"-avt.avi", self.backupFolder)
                        print "AVT movie file successfully backed up. \nBacking up AVT frame interval file ..."
                        shutil.copy2(os.path.join(self.saveFolder,self.outputFileName)+"-avt.txt", self.backupFolder)
                        print "AVT frame interval file successfully backed up. \n\n"
                
                print "Finished recording at: ", str(datetime.datetime.now())
                print "Elapsed time: ",time.clock()-start, "seconds\n"


    def shutdown(self):
        # Release everything if job is finished
        print "Program closing."
        try:
            for c in self.cap:
                c.release()
                print "camera released"
        except:
                pass

        try:
            if self.avt:
                self.avt.release()
                print "AVT camera released"
        except:
            pass
        
        
        try:
            for o in self.out:
                o.release()
                print "Videowriter released..."
        except:
                pass
        try:
            for f in self.frameoutput:
                f.close()
                print "Frame interval output closed..."
        except:
                pass
            
        
        if self.backupFolder:
            # Check if backup folder exists, if not creat one
            if not os.path.exists(os.path.dirname(self.backupFolder)):
                os.mackdirs(os.path.dirname(self.backupFolder))
                
            try:
                for i,c in enumerate(self.cap):
                    shutil.copy2(os.path.join(self.saveFolder,self.outputFileName)+"-%i.avi"%i, self.backupFolder)
                    print "Movie file successfully backed up. \nBacking up frame interval file ..."
                    shutil.copy2(os.path.join(self.saveFolder,self.outputFileName)+"-%i.txt"%i, self.backupFolder)
                    print "Frame interval file successfully backed up. \n\n"
            except:
                pass
            
            if self.avt:
                try:
                    shutil.copy2(os.path.join(self.saveFolder,self.outputFileName)+"-avt.avi", self.backupFolder)
                    print "AVT movie file successfully backed up. \nBacking up AVT frame interval file ..."
                    shutil.copy2(os.path.join(self.saveFolder,self.outputFileName)+"-avt.txt", self.backupFolder)
                    print "AVT frame interval file successfully backed up. \n\n"
                except:
                    pass
                        

            
        time.sleep(1)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    wcr = WebcamRecorder()
    params = {
        'cameras':2,
        'size':(800,600),
        'exposure':-6,
        'brightness':100,
        'contrast':5,
        'saturation':82,
    }
    
    print params
    atexit.register(wcr.shutdown)
    wcr.run(**params)
    
