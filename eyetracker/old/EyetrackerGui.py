'''
Created on Oct 18, 2012

@author: derricw

Displays a GUI for adjusting camera parameters and thresholds for pruning out the LED
    and pupil on an Eyetracker object instance.

'''

 
import sys
import os
import io
import ConfigParser
import datetime
import time
from PyQt4 import QtCore, QtGui
from EyetrackerLayout import Ui_MainWindow
try:
    from aibs.iodaq import AnalogOutput as AO
except Exception,e:
    print "Couldn't initialize analog output...",e
import numpy as np
import socket

from EyetrackerCV2 import Eyetracker
 
DEFAULTCONFIG = """
[EyetrackerGUI]
camera = None
video = None
targetip = "127.0.0.1"
targetport = 10001
videooutput = r"C:/AibStim/eyetracking"
secondary = None

[Eyetracker]
blur = 0
ledthresh = 253
pupilthresh = 221
ledsize = [10,1400]
pupilsize = [200,10000]
roi = None
led_roi = None

[Gazetracker]
monitorsize = (49,25)
monitorresolution = (1920,1080)
monitordistance = 15.0
ledy = 12.0
camfov = 3.01
eyeradius = 0.165

""" 
 
class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #ETC
        self.output = False
        self.framecount = 0
        
        #GET CONFIG
        config = {}
        defaults = ConfigParser.RawConfigParser()
        defaults.readfp(io.BytesIO(DEFAULTCONFIG))
        for (k,v) in defaults.items("EyetrackerGUI"):
            config[k]=eval(v)
        #MERGE WITH LOCAL FILE
        try:
            path = r"C:/AibStim/config/eyetracking.cfg"
            if os.path.exists(path):
                
                localconfig = ConfigParser.RawConfigParser()
                localconfig.read(path)
                for (k,v) in localconfig.items("EyetrackerGUI"):
                    config[k]=eval(v)
            else:
                print "Creating new config file:",path
                with open(path,'w+') as f:
                    f.write(DEFAULTCONFIG)
        except Exception, e:
            print "Error reading config file %s: "%(path),e
        
        #Connect signals
        self.ui.horizontalSlider_general_blur.sliderMoved.connect(self._blurSlider)
        self.ui.horizontalSlider_general_zoom.sliderMoved.connect(self._zoomSlider)
        self.ui.horizontalSlider_led_binary.sliderMoved.connect(self._ledBinarySlider)
        self.ui.horizontalSlider_led_min.sliderMoved.connect(self._ledMinSlider)
        self.ui.horizontalSlider_led_max.sliderMoved.connect(self._ledMaxSlider)
        self.ui.horizontalSlider_pupil_binary.sliderMoved.connect(self._pupilBinarySlider)
        self.ui.horizontalSlider_pupil_min.sliderMoved.connect(self._pupilMinSlider)
        self.ui.horizontalSlider_pupil_max.sliderMoved.connect(self._pupilMaxSlider)
        self.ui.horizontalSlider_camera_hue.sliderMoved.connect(self._cameraHueSlider)
        self.ui.horizontalSlider_camera_saturation.sliderMoved.connect(self._cameraSaturationSlider)
        self.ui.horizontalSlider_camera_brightness.sliderMoved.connect(self._cameraBrightnessSlider)
        self.ui.horizontalSlider_camera_gain.sliderMoved.connect(self._cameraGainSlider)
        self.ui.horizontalSlider_camera_contrast.sliderMoved.connect(self._cameraContrastSlider)
        self.ui.horizontalSlider_camera_exposure.sliderMoved.connect(self._cameraExposureSlider)
        self.ui.pushButton_output.clicked.connect(self._outputToggle)
        self.ui.checkBox_triangle.clicked.connect(self._triangleToggle)
        self.ui.radioButton_angleLed.clicked.connect(self._outputFormatSelect)
        self.ui.radioButton_angleScreen.clicked.connect(self._outputFormatSelect)
        self.ui.radioButton_pixelsScreen.clicked.connect(self._outputFormatSelect)
        self.ui.radioButton_displayLED.clicked.connect(self._setDisplayLED)
        self.ui.radioButton_displayPupil.clicked.connect(self._setDisplayPupil)
        self.ui.radioButton_displayBoth.clicked.connect(self._setDisplayBoth)
        self.ui.checkBox_showProcessing.clicked.connect(self._showProcessingToggle)
        self.ui.pushButton_saveConfig.clicked.connect(self._saveConfig)

        #Create Eyetracker
        print "Starting eyetracker..."
        print config
        self.et = Eyetracker(camera=config['camera'],video=config['video'])
        
        
        #Create secondary camera
        if config['secondary']:
            print "Starting secondary camera..."
            from Webcam import Webcam
            self.secondary = Webcam()
        else:
            self.secondary = None

        #Set initial slider bar states (might should be before signals)
        self.ui.horizontalSlider_general_blur.setValue(self.et.blur)
        self.ui.horizontalSlider_general_zoom.setValue(self.et.zoom)
        self.ui.horizontalSlider_led_binary.setValue(self.et.ledthresh)
        self.ui.horizontalSlider_led_min.setValue(self.et.ledsize[0])
        self.ui.horizontalSlider_led_max.setValue(self.et.ledsize[1])
        self.ui.horizontalSlider_pupil_binary.setValue(self.et.pupilthresh)
        self.ui.horizontalSlider_pupil_min.setValue(self.et.pupilsize[0])
        self.ui.horizontalSlider_pupil_max.setValue(self.et.pupilsize[1])

        #Set initial label states
        self.ui.label_image.setPixmap(QtGui.QPixmap('res/ledAngle.png'))
        self.ui.pushButton_output.setStyleSheet("QPushButton { background-color: rgb(0,255,0);}")

        #and for the camera...
        #self.ui.horizontalSlider_camera_hue.setValue(
        #    self.et.camproperties['hue'])
        self.ui.horizontalSlider_camera_saturation.setValue(
            self.et.camproperties['saturation'])
        self.ui.horizontalSlider_camera_brightness.setValue(
            self.et.camproperties['brightness'])
        #self.ui.horizontalSlider_camera_gain.setValue(
        #    self.et.camproperties['gain'])
        self.ui.horizontalSlider_camera_contrast.setValue(
            self.et.camproperties['contrast'])
        self.ui.horizontalSlider_camera_exposure.setValue(
            self.et.camproperties['exposure'])

        #Timer setup
        self.ctimer = QtCore.QTimer()
        self.ctimer.timeout.connect(self._tick)
        self.ctimer.start(1) #run as fast as possible 1ms minimum

        #Analog Output setup
        try:
            self.ao = AO("Dev1",channels=[0,1])
            self.ao.StartTask()
            data = np.array([0,0],dtype=np.float)
            self.ao.Write(data)
        except Exception,e:
            self.ao = False
            print "Could not initialize analog output.",e
            
        #Set up trigger/output socket
        self.IP = '0.0.0.0'
        self.PORT = 10001
        self.TARGETIP = config['targetip']
        self.TARGETPORT = config['targetport']
        print "Incoming Port:",self.PORT
        print "Outgoing Port:",self.TARGETPORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.IP,self.PORT))
        self.sock.settimeout(0.0)
        
        self.videoFileName = None
        self.saveFolder = config['videooutput']
        
    def _saveConfig(self):
        print "Saving config:"
        try:
            path = r"C:/AibStim/config/eyetracking.cfg"
            cfp = ConfigParser.RawConfigParser()
            cfp.read(path)
            cfp.set("Eyetracker", "ledthresh", str(self.et.ledthresh))
            cfp.set("Eyetracker", "pupilthresh", str(self.et.pupilthresh))
            cfp.set("Eyetracker", "ledsize", str(self.et.ledsize))
            cfp.set("Eyetracker", "pupilsize", str(self.et.pupilsize))
            cfp.set("Eyetracker", "roi", str(self.et.roi))
            cfp.set("Eyetracker", "led_roi", str(self.et.led_roi))
            print cfp.items("Eyetracker")
            with open(path,'wb') as configfile:
                cfp.write(configfile)
        except Exception, e:
            print "Couldn't save configuration:", e

    def _setDisplayPupil(self):
        self.et.displayMode = 2
        
    def _setDisplayLED(self):
        self.et.displayMode = 1
        
    def _setDisplayBoth(self):
        self.et.displayMode = 0

    def _blurSlider(self):
        self.et.blur = int(self.ui.horizontalSlider_general_blur.value())

    def _zoomSlider(self):
        self.et.zoom = int(self.ui.horizontalSlider_general_zoom.value())

    def _ledBinarySlider(self):
        self.et.ledthresh = int(self.ui.horizontalSlider_led_binary.value())

    def _ledMinSlider(self):
        newval = int(self.ui.horizontalSlider_led_min.value())
        if newval <= self.et.ledsize[1]:
            self.et.ledsize[0] = newval

    def _ledMaxSlider(self):
        newval = int(self.ui.horizontalSlider_led_max.value())
        if newval >= self.et.ledsize[0]:
            self.et.ledsize[1] = newval

    def _pupilBinarySlider(self):
        self.et.pupilthresh = int(self.ui.horizontalSlider_pupil_binary.value())

    def _pupilMinSlider(self):
        newval = int(self.ui.horizontalSlider_pupil_min.value())
        if newval <= self.et.pupilsize[1]:
            self.et.pupilsize[0] = newval

    def _pupilMaxSlider(self):
        newval = int(self.ui.horizontalSlider_pupil_max.value())
        if newval >= self.et.pupilsize[0]:
            self.et.pupilsize[1] = newval

    def _cameraHueSlider(self):
        pass

    def _cameraSaturationSlider(self):
        self.et.camproperties['saturation'] = int(
            self.ui.horizontalSlider_camera_saturation.value())
        self.et.setCamProp('saturation')

    def _cameraBrightnessSlider(self):
        self.et.camproperties['brightness'] = int(
            self.ui.horizontalSlider_camera_brightness.value())
        self.et.setCamProp('brightness')

    def _cameraGainSlider(self):
        pass

    def _cameraContrastSlider(self):
        self.et.camproperties['contrast'] = int(
            self.ui.horizontalSlider_camera_contrast.value())
        self.et.setCamProp('contrast')

    def _cameraExposureSlider(self):
        self.et.camproperties['exposure'] = int(
            self.ui.horizontalSlider_camera_exposure.value())
        self.et.setCamProp('exposure')

    def _tick(self):
        try:
            self.et.nextFrame()
            if self.secondary:
                self.secondary.nextFrame()
            self.framecount+=1
            try:
                self.gaze = self.et.getGaze()
                self.alldata = self.et.getAllData()
                if self.framecount% 5 == 0:
                    if self.gaze:
                        self.ui.label_azimuth.setText(str(self.gaze[0]))
                        self.ui.label_zenith.setText(str(self.gaze[1]))
                        self.ui.label_pupil.setText(str(self.gaze[2]))
                        self.ui.label_fps.setText(str(self.et._tock))
                    if self.alldata:
                        self.ui.label_pupilPosition.setText(str(self.alldata[1]))
                        self.ui.label_ledPosition.setText(str(self.alldata[0]))
                    self.framecount = 0
            except:
                pass
            if self.output:
                self._output()
        except Exception, e:
            print e
            #self.et.getCamera()
        self._checkUDP()


    def _triangleToggle(self):
        if self.ui.checkBox_triangle.isChecked():
            self.et.showTriangle=True
        else:
            self.et.showTriangle=False
            
    def _showProcessingToggle(self):
        if self.ui.checkBox_showProcessing.isChecked():
            self.et.showProcessing=True
        else:
            self.et.showProcessing=False

    def _output(self):

        if self.ui.checkBox_toFile.isChecked():
            out = str(self.gaze)+'\n'
            self.outputfile.write(out)
        if self.ui.checkBox_toVideo.isChecked():
            t=str(time.clock())+"\n"
            self.frameoutput.write(t)
            if self.secondary:
                self.secondaryframeintervals.write(t)
        if self.ui.checkBox_toConsole.isChecked():
            print self.gaze
            pass
        if self.ui.checkBox_toAnalogOut.isChecked():
            if self.ao:
                out=self.deg2volts(self.gaze[:2])
                self.ao.Write(out)
        if self.ui.checkBox_toUDP.isChecked():
            self.sock.sendto(str(self.gaze),(self.TARGETIP,self.TARGETPORT))

    def _outputToggle(self):
        if self.output:
            self.output=False
            try:
                self.outputfile.close()
            except Exception, e:
                pass
            try:
                self.et.stopVideo()
                self.videoFileName=None
                self.frameoutput.close()
            except Exception, e:
                print e
            try:
                if self.secondary:
                    self.secondary.stopVideo()
                    self.secondaryframeintervals.close()
            except Exception, e:
                print e
            self.ui.pushButton_output.setStyleSheet("QPushButton { background-color: rgb(0,255,0);}")
        else:
            if self.ui.checkBox_toFile.isChecked():
                outdir = str(self.ui.lineEdit_output.text())
                self.outputfile = open(outdir,'w+')
            if self.ui.checkBox_toVideo.isChecked():
                if self.videoFileName:
                    videoname = os.path.join(self.saveFolder,self.videoFileName)
                    frameintervals = os.path.join(self.saveFolder,self.videoFileName)
                else:
                    dt = datetime.datetime.now()
                    videoname = os.path.join(self.saveFolder, dt.strftime('%y%m%d%H%M%S'))
                    frameintervals = os.path.join(self.saveFolder, dt.strftime('%y%m%d%H%M%S'))
                videoname+="-0.avi"
                frameintervals+="-0.txt"
                print videoname
                print frameintervals
                if self.secondary:
                    secondaryvideoname=videoname[:-5]+"1.avi"
                    secondaryframeintervals=frameintervals[:-5]+"1.txt"
                self.et.startVideo(videoname)
                self.frameoutput = open(frameintervals,'w')
                if self.secondary:
                    self.secondary.startVideo(secondaryvideoname)
                    self.secondaryframeintervals = open(secondaryframeintervals,'w')
            self.output=True
            self.ui.pushButton_output.setStyleSheet("QPushButton { background-color: rgb(255,0,0);}")

    def _outputFormatSelect(self):
        if self.ui.radioButton_angleLed.isChecked():
            self.ui.label_image.setPixmap(QtGui.QPixmap('res/ledAngle.png'))
        elif self.ui.radioButton_angleScreen.isChecked():
            self.ui.label_image.setPixmap(QtGui.QPixmap('res/screenAngle.png'))
        elif self.ui.radioButton_pixelsScreen.isChecked():
            self.ui.label_image.setPixmap(QtGui.QPixmap('res/screenPixel.png'))
            
    def _checkUDP(self):
        try:
            data, addr = self.sock.recvfrom(1024)
            if data[0]=="1":
                if len(data) > 1:
                    self.videoFileName = data[1:]
                if self.output == False:
                    self._outputToggle()
                    print "OUTPUT STARTING!"
            elif data[0]=="0":
                if self.output:
                    self._outputToggle()
                    print "OUTPUT STOPPING!"
        except:
            pass

    def closeEvent(self,evnt):
        self.ctimer.stop()
        self.et.close()
        if self.secondary:
            self.secondary.close()
        if self.ao:
            self.ao.ClearTask()
        print "CLOSING..."

    def deg2volts(self,gaze):
        npgaze = np.array(gaze,dtype=np.float64)/90*2.5+2.5 # -90 to +90 -> 0 to 5
        return npgaze



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())