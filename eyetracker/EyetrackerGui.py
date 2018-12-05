#!/usr/bin/env python
'''
eyetrackergui.py

Allen Institute for Brain Science

Created on Oct 3, 2014

@author: derricw

Displays a GUI for adjusting video parameters and thresholds for pruning out the LED
    and pupil on an video stream.

Main purpose is to load eyetracking videos and process them.

CLI counterpart is "eyetracker.py"

'''
import sys
import os
import io
import configparser as ConfigParser
import time
from PyQt5 import QtCore, QtGui
import numpy as np
import platform

import pyqtgraph as pg

from image_processor import ImageProcessor
from mainwindow_layout import Ui_MainWindow
from video_view import VideoView as Video
from plot_view import PlotView

if platform.system().lower() in ['linux', 'darwin']:
    HOME = os.path.expanduser("~/eyetracker")
    CONFIG_PATH = os.path.join(HOME, "config/eyetracking.cfg")
    VIDEO_DIR = os.path.join(HOME, "videos")
    if platform.system().lower() == 'linux':
        #linux command to open in new terminal
        COMMAND_PREFIX = "gnome-terminal -e 'bash -c python"
        COMMAND_SUFFIX = "'"
    else:
        #mac command to open in new terminal
        COMMAND_PREFIX = "open -n -a python --args"
        COMMAND_SUFFIX = ""
else:
    #windows
    CONFIG_PATH = "C:/eyetracker/config/eyetracking.cfg"
    VIDEO_DIR = "C:/eyetracker/videos"
    COMMAND_PREFIX = "start {}".format(sys.executable)
    COMMAND_SUFFIX = ""

def checkDirs(*args):
    ##TODO move this to a utilities file
    """ Checks to see if any of the directories exist.  Creates them if they don't"""
    for arg in [x for x in args if x is not None]:
        if not os.path.isdir(arg):
            os.makedirs(arg)
            print("Creating new path:", arg)

checkDirs(os.path.split(CONFIG_PATH)[0], VIDEO_DIR)

DEFAULTCONFIG = """
[Eyetracker]
led_roi = (125, 75, 225, 170)
pupil_roi = (40, 40, 300, 200)
pupil_blur = 2
pupil_dilate = 4
pupil_erode = 5
mask_circle_thickness = 40
pupil_binary_thresh = 210
pupil_min_size = 100
led_binary_thresh = 200
equalize = False
led_mask_circle_thickness = 5
led_min_size = 1

[Calibration]
mm_per_pix = 0.085

"""

ABOUT = """
Allen Institute for Brain Science
author: derricw
updated: at some point
"""

CURR_DIR = os.path.dirname(os.path.realpath(__file__))


class EyetrackerGui(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #setup eyetracker
        self._setupEyetracker()

        #Setup buttons
        self._setupUiSlots()

        #Setup graphics
        self.video_view = Video()
        self.video_view.move(300, 200)
        self.video_view.show()
        self.video_view.set_roi_geometry(led_roi=self.eyetracker.led_roi,
                                         pupil_roi=self.eyetracker.pupil_roi)
        self.video_view.pupil_roi.sigRegionChanged.connect(self._newPupilROI)
        self.video_view.led_roi.sigRegionChanged.connect(self._newLedROI)

        self.plotting_window = None

        self._setupGraphics()

        #Current video file or camera stream that we are processing
        self.video_file = None
        self.video_path = None
        self.show_positions = True
        self.pause = False

        #GET CONFIG AND APPLY IT
        self.config_path = None
        defaults = self._get_default_config()
        self._apply_config(defaults)
        self.custom_algorithm = None

        #Timer setup
        self.ctimer = QtCore.QTimer()
        self.ctimer.timeout.connect(self._tick)
        self.ctimer.start(30)  # run as fast as possible 1ms minimum
        self.last_tick = time.clock()

    def _get_default_config(self):
        """
        Returns the default configuration for the GUI.

        First reads defaults from DEFAULTCONFIG, then merges with
            local config file.
        """
        config = {}
        defaults = ConfigParser.RawConfigParser()
        defaults.readfp(io.BytesIO(DEFAULTCONFIG))
        for (k, v) in defaults.items("Eyetracker"):
            config[k] = eval(v)

        #MERGE WITH LOCAL FILE
        try:
            path = CONFIG_PATH
            if os.path.exists(path):

                localconfig = ConfigParser.RawConfigParser()
                localconfig.read(path)
                for (k, v) in localconfig.items("Eyetracker"):
                    config[k] = eval(v)
            else:
                print("Creating new config file:", path)
                with open(path, 'w+') as f:
                    f.write(DEFAULTCONFIG)
        except Exception as e:
            print("Error reading config file %s: " % (path), e)
        return config

    def _setupUiSlots(self):
        """
        Sets up all button and widget callbacks for the GUI.
        """
        # Menu
        self.ui.action_load_movie.triggered.connect(self._load_movie_clicked)
        self.ui.action_save_avi.triggered.connect(self._save_avi_clicked)
        self.ui.action_save_hdf5.triggered.connect(self._save_hdf5_clicked)
        self.ui.actionPlots.triggered.connect(self._show_plots_clicked)
        self.ui.actionQuit.triggered.connect(self._quit_clicked)
        self.ui.actionSettings.triggered.connect(self._settings_clicked)
        self.ui.actionAbout.triggered.connect(self._about_clicked)
        self.ui.actionVideo.triggered.connect(self._show_video_clicked)
        self.ui.action_custom_algorithm.triggered.connect(self._custom_algorithm_clicked)

        # Slider bars
        self.ui.horizontalSlider_general_blur.valueChanged.connect(self._blur_slider_changed)
        self.ui.horizontalSlider_general_dilation.valueChanged.connect(self._dilation_slider_changed)
        self.ui.horizontalSlider_general_erosion.valueChanged.connect(self._erosion_slider_changed)
        self.ui.horizontalSlider_pupil_binary.valueChanged.connect(self._pupil_binary_slider_changed)
        self.ui.horizontalSlider_led_binary.valueChanged.connect(self._led_binary_slider_changed)
        self.ui.horizontalSlider_pupil_min.valueChanged.connect(self._pupil_min_slider_changed)
        self.ui.horizontalSlider_pupil_mask_circle.valueChanged.connect(self._pupil_mask_slider_changed)
        self.ui.horizontalSlider_led_min.valueChanged.connect(self._led_min_slider_changed)
        self.ui.horizontalSlider_led_mask_circle.valueChanged.connect(self._led_mask_slider_changed)

        # Check boxes
        self.ui.checkBox_showProcessing.clicked.connect(self._show_processing_clicked)
        self.ui.checkBox_markup.clicked.connect(self._show_markup_clicked)
        self.ui.checkBox_equalize.clicked.connect(self._equalize_clicked)

        # Buttons
        self.ui.pushButton_pauseplay.clicked.connect(self._pause_clicked)
        self.ui.pushButton_process.clicked.connect(self._process_clicked)
        self.ui.pushButton_saveConfig.clicked.connect(self._save_config_clicked)
        self.ui.pushButton_loadConfig.clicked.connect(self._load_config_clicked)


    def _setupGraphics(self):
        """
        Sets up any graphics windows that aren't separate widgets.
        """
        self.processing_window = None

    def _setupEyetracker(self):
        """
        Sets up the image processor for pupil/led detection.
        """
        self.eyetracker = ImageProcessor()

    def _apply_config(self, config):
        """
        Applies a configuration set.  Adjusts both current image processor
            instance and GUI's video display ROI

        Parameters
        ----------
        config : dict
            Dictionary of values to set in the image processor see DEFAULTCONFIG

        """
        # sets eyetracker config
        self._set_eyetracker_config(config)
        pupil_roi = config['pupil_roi']
        led_roi = config['led_roi']

        # sets Video display ROI sizes
        if self.video_file:
            # test_img = self.video_file.getFrame(0)
            test_img = self.video_file.getImage()
            height = test_img.height
            if pupil_roi:
                pupil_roi = (pupil_roi[0], height-pupil_roi[3],
                             pupil_roi[2], height-pupil_roi[1])
            if led_roi:
                led_roi = (led_roi[0], height-led_roi[3],
                           led_roi[2], height-led_roi[1])
        self.video_view.set_roi_geometry(pupil_roi=pupil_roi, led_roi=led_roi)

        # sets slider bar values
        self.ui.horizontalSlider_led_binary.setValue(config['led_binary_thresh'])
        self.ui.horizontalSlider_general_blur.setValue(config['pupil_blur'])
        self.ui.horizontalSlider_general_erosion.setValue(config['pupil_erode'])
        self.ui.horizontalSlider_general_dilation.setValue(config['pupil_dilate'])
        self.ui.horizontalSlider_pupil_binary.setValue(config['pupil_binary_thresh'])
        self.ui.horizontalSlider_led_mask_circle.setValue(config['led_mask_circle_thickness'])
        self.ui.horizontalSlider_pupil_mask_circle.setValue(config['mask_circle_thickness'])
        self.ui.horizontalSlider_led_min.setValue(config['led_min_size'])
        self.ui.horizontalSlider_pupil_min.setValue(config['pupil_min_size'])

        # sets check boxes
        self.ui.checkBox_equalize.setChecked(config['equalize'])

    def _tick(self):
        """
        GUI update callback.

        If there is a video being displayed, we process the next frame,
            update labels, update plots, update video display.

        """
        if self.video_file:
            try:

                frame = self.video_file.getImage()
                if frame.size() == (0, 0):
                    print('replay from start ...')
                    self._loadVideo(self.video_path)
                    frame = self.video_file.getImage()
                frame = self._processFrame(frame)

                self._updateLabels()

                self._showFrame(frame)

                if self.processing_window:
                    self._updateProcessingWindow()

                if self.plotting_window:
                    self._updatePlotWindow()
            except AttributeError as e:
                print("Rewinding video...")
                self.video_file.rewind()
            except Exception as e:
                print(type(e), e)

        t = time.clock()
        self.ui.label_fps.setText(str(1/(t-self.last_tick))[:5])
        self.last_tick = t

    def _processFrame(self, frame):
        """
        Processes the current frame and prepares it for display.

        Parameters
        ----------
        frame : SimpleCV.Image
            Image to process

        Returns
        -------
        SimpleCV.Image
            Processed image

        """
        ##TODO: restructure this because all this stuff shouldn't be in here
        frame = self.eyetracker.preprocess(frame)
        self.led = self.eyetracker.find_led(frame)
        self.pupil = self.eyetracker.find_pupil(frame)

        if self.led:
            self.led_pos = self.eyetracker.get_led_pos()
        else:
            self.led_pos = None
        if self.pupil:
            self.pupil_pos = self.eyetracker.get_pupil_pos()
            self.pupil_area = self.pupil.area()
        else:
            self.pupil_pos = None
            self.pupil_area = None

        if self.show_positions:
            ##TODO: Move this to IP
            if self.led:
                frame.drawCircle(self.led_pos,
                                 self.led.radius(),
                                 color=(255, 0, 0),
                                 thickness=min(self.led.radius(), 2))
            if self.pupil:
                frame.drawCircle(self.pupil_pos,
                                 self.pupil.radius(),
                                 color=(0, 255, 0),
                                 thickness=min(self.pupil.radius(), 2))
            try:
                frame = frame.applyLayers()
            except Exception as e:
                print("Couldn't apply layers:", e)
        return frame

    def _updateLabels(self):
        """
        Updates the labels on the GUI
        """
        if self.pupil_pos:
            self.ui.label_pupilPosition.setText(str(self.pupil_pos))
        if self.pupil_area:
            self.ui.label_pupil_area.setText(str(self.pupil_area))
        if self.led_pos:
            self.ui.label_ledPosition.setText(str(self.led_pos))

    def _updateProcessingWindow(self):
        """
        Updates the processing window with the current frame.
        """
        intermediate_step = str(self.ui.comboBox_processing.currentText())
        processing_img = getattr(self.eyetracker, intermediate_step)
        processing_img = np.fliplr(processing_img.getNumpy())
        self.processing_image.setImage(processing_img)

    def _updatePlotWindow(self):
        """
        Updates the plotting window with the data from the current frame
        """
        self.plotting_window.addFrame(led_pos=self.led_pos,
                                      pupil_pos=self.pupil_pos,
                                      pupil_area=self.pupil_area)

    def _showFrame(self, frame):
        """
        Shows the current frame.  Flips it because Qt and numpy have
            different coordinate systems.
        """
        img = np.fliplr(frame.getNumpy())
        self.video_view.img.setImage(img)

    def _newPupilROI(self, event):
        """
        Callback for a pupil ROI change.
        """
        pos = tuple(event.pos())
        size = tuple(event.size())
        # y is reversed because numpy and Qt hate each other
        if self.video_file:
            self._set_pupil_roi(pos, size)

    def _blur_slider_changed(self, event):
        """ Blur slider callback. """
        self.eyetracker.pupil_blur = int(event)

    def _erosion_slider_changed(self, event):
        """ Erosion slider callback. """
        self.eyetracker.pupil_erode = int(event)

    def _dilation_slider_changed(self, event):
        """ Dilation slider callback. """
        self.eyetracker.pupil_dilate = int(event)

    def _pupil_binary_slider_changed(self, event):
        """ Pupil binary threshold slider callback. """
        self.eyetracker.pupil_binary_thresh = int(event)

    def _led_binary_slider_changed(self, event):
        """ LED binary threshold slider callback. """
        self.eyetracker.led_binary_thresh = int(event)

    def _led_min_slider_changed(self, event):
        """ LED min size slider callback. """
        self.eyetracker.led_min_size = int(event)

    def _led_mask_slider_changed(self, event):
        """ LED mask slider callback. """
        self.eyetracker.led_mask_circle_thickness = int(event)

    def _pupil_mask_slider_changed(self, event):
        """ Pupil mask slider callback. """
        self.eyetracker.mask_circle_thickness = int(event)

    def _pupil_min_slider_changed(self, event):
        """ Pupil min size slider callback. """
        self.eyetracker.pupil_min_size = int(event)

    def _equalize_clicked(self, event):
        """ Equalize checkbox callback. """
        self.eyetracker.equalize = bool(event)

    def _show_processing_clicked(self, event):
        """
        Creates a temporary graphics window for showing processing steps.
        """
        if event:
            self.processing_window = pg.GraphicsLayoutWidget()
            view = self.processing_window.addViewBox()
            view.setAspectLocked(True)
            view.enableAutoRange(True)
            img = pg.ImageItem()
            view.addItem(img)
            self.processing_image = img
            self.processing_window.show()
        else:
            if self.processing_window:
                self.processing_window.close()
                self.processing_window = None
                self.processing_image = None

    def _show_video_clicked(self, event):
        """
        Callback for the video display window button.
        """
        self.video_view.show()

    def _show_plots_clicked(self, event):
        """
        Callback for the plot display window button.
        """
        self.plotting_window = PlotView()
        self.plotting_window.show()

    def _custom_algorithm_clicked(self):
        """
        Callback for the load -> custom algorithm button.
        """
        algorithm_path = str(QtGui.QFileDialog.getOpenFileName(self,
                             "Select a config file",
                             "."))
        if algorithm_path:
            self._load_custom_algorithm(algorithm_path)
        else:
            return

    def _show_markup_clicked(self, event):
        """
        Callback for show markup button.
        """
        self.show_positions = bool(event)

    def _pause_clicked(self):
        """
        Callback for clicking pause button.  Stops and starts update timer,
            and changes the button icon.
        """
        if self.pause:
            self.ctimer.start(30)
            self.pause = False
            self.ui.pushButton_pauseplay.setIcon(QtGui.QIcon("res/pause.png"))
        else:
            self.ctimer.stop()
            self.pause = True
            self.ui.pushButton_pauseplay.setIcon(QtGui.QIcon("res/play.png"))

    def _process_clicked(self):
        """
        Process whole movie button callback.

        """
        self._save_config_clicked()
        self._save_hdf5(dialog=False)

    def _save_config_clicked(self):
        """
        Saves the current configuration for the current video.  Creates a
            file if necessary.
        """
        config = self._get_eyetracker_config()

        print(config)

        video_path = self.video_path
        filename, ext = os.path.splitext(video_path)

        config_path = filename+".cfg"

        parser = ConfigParser.RawConfigParser()
        parser.add_section("Eyetracker")
        for k, v in config.iteritems():
            parser.set("Eyetracker", k, v)

        with open(config_path, 'w+') as f:
            parser.write(f)

        self.config_path = config_path


    def _get_eyetracker_config(self):
        """
        Returns the current image processor configuration.
        """
        config = {
            'led_roi': self.eyetracker.led_roi,
            'pupil_roi': self.eyetracker.pupil_roi,
            'pupil_blur': self.eyetracker.pupil_blur,
            'pupil_dilate': self.eyetracker.pupil_dilate,
            'pupil_erode': self.eyetracker.pupil_erode,
            'mask_circle_thickness': self.eyetracker.mask_circle_thickness,
            'pupil_binary_thresh': self.eyetracker.pupil_binary_thresh,
            'led_binary_thresh': self.eyetracker.led_binary_thresh,
            'equalize': self.eyetracker.equalize,
            'led_mask_circle_thickness': self.eyetracker.led_mask_circle_thickness,
            'led_min_size': self.eyetracker.led_min_size,
            'pupil_min_size': self.eyetracker.pupil_min_size,

        }
        return config

    def _set_eyetracker_config(self, config):
        """
        Sets the current eyetracker configuration.
        """
        for k, v in config.iteritems():
            setattr(self.eyetracker, k, v)

    def _load_config_clicked(self):
        """
        Callback for load config button.  Lets the user load a custom
            configuration file from a load file dialog window.
        """
        config_path = str(QtGui.QFileDialog.getOpenFileName(self,
                          "Select a config file",
                          VIDEO_DIR))
        if config_path:
            self._load_config(config_path)

    def _load_config(self, config_path):
        """
        Loads a config from a specified path.

        Parameters
        ----------
        config_path : str
            full path of config file.

        """
        self.config_path = config_path
        parser = ConfigParser.RawConfigParser()
        parser.read(config_path)
        section = parser.items("Eyetracker")
        config = {}
        for k, v in section:
            config[k] = eval(v)
        self._apply_config(config)

    def _load_custom_algorithm(self, path):
        """
        Loads a custom image processing algorithm.
        """
        try:
            import imp
            ip = imp.load_source('image_processor', path)
            #save a copy of current eyetracker's configuration
            config = self._get_eyetracker_config()

            self.eyetracker = ip.ImageProcessor()

            #setup new eyetracker with same configuration
            self._set_eyetracker_config(config)
            self.custom_algorithm = path
            print("Successfully loaded custom algorithm")
        except Exception as e:
            print("Error loading custom algorithm: ", type(e), e)

    def _set_pupil_roi(self, pos, size):
        """
        Sets the pupil ROI in the eyetracker.  Performs the Qt-numpy flip

        Parameters
        ----------
        pos : tuple (x,y)
            roi position (lower left corner)
        size : tuple (w,h)
            roi width, height

        """
        # img_height = self.video_file.getFrame(0).height
        img_height = self.video_file.getImage().height
        self.eyetracker.set_pupil_roi(pos[0],
                                      img_height-(pos[1]+size[1]),
                                      pos[0]+size[0],
                                      img_height-pos[1])

    def _newLedROI(self, event):
        """
        Callback for an LED ROI change.

        """
        pos = tuple(event.pos())
        size = tuple(event.size())
        if self.video_file:
            self._set_led_roi(pos, size)

    def _set_led_roi(self, pos, size):
        """
        Sets the LED ROI in the eyetracker.  Performs the Qt-numpy flip

        See _set_pupil_roi for details.

        """
        # img_height = self.video_file.getFrame(0).height
        img_height = self.video_file.getImage().height
        self.eyetracker.set_led_roi(pos[0],
                                    img_height-(pos[1]+size[1]),
                                    pos[0]+size[0],
                                    img_height-pos[1])

    def _loadVideo(self, path):
        """
        Loads a video from a specified path.
        """
        self.video_file = VirtualCamera(path, "video")
        self.video_path = path
        # frame0 = self.video_file.getFrame(0)
        frame0 = self.video_file.getImage()
        img = np.fliplr(frame0.getNumpy())
        self.video_view.set_image_format(img.shape)
        self.setWindowTitle(self.video_path)

    def closeEvent(self, evnt):
        """
        Window close event callback.
        """
        self.ctimer.stop()
        self.video_view.close()
        if self.processing_window:
            self.processing_window.close()
        if self.plotting_window:
            self.plotting_window.close()
        print("CLOSING...")
        sys.exit()

    def _quit_clicked(self):
        """
        Quit menu button callback.
        """
        print("QUIT")
        self.closeEvent(None)

    def _settings_clicked(self):
        """
        Settings menu button callback.
        """
        pass

    def _about_clicked(self):
        """
        About menu button callback.
        """
        try:
            from eyetracker import __version__
        except:
            __version__ = "?"
        response = QtGui.QMessageBox.about(self, "Camera Viewer version %s" %
                                           __version__, ABOUT)

    def _load_movie_clicked(self):
        """
        Load movie button callback.
        """
        video_path = str(QtGui.QFileDialog.getOpenFileName(self,
                         "Select a video file", VIDEO_DIR))
        if video_path:
            self._loadVideo(video_path)
            filename, ext = os.path.splitext(video_path)
            config_path = filename+".cfg"
            try:
                with open(config_path) as f:
                    f.read()
                self._load_config(config_path)
            except IOError as e:
                print("No config file for this movie, using defaults...", e)

        else:
            pass

    def _load_hdf5_clicked(self):
        """
        Load HDF5 menu button callback.
        """
        pass

    def _load_tiff_clicked(self):
        """
        Load tiff stack menu button callback.
        """
        pass

    def _save_avi_clicked(self):
        """
        Save avi menu button callback.
        """
    #     if self.video_path:
    #         self._save_avi(dialog=False)
        pass

    def _save_avi(self, dialog=True):
        """ Saves an AVI.  Guesses ouput path if no dialog requested. """
        # if dialog:
        #     output_path = str(QtGui.QFileDialog.getSaveFileName(self,
        #                       "Save AVI as",
        #                       VIDEO_DIR,
        #                       filter="AVI (*.avi)"))
        # else:
        #     filename, ext = os.path.splitext(self.video_path)
        #     output_path = "%s-output.avi" % (filename)
        # if output_path:
        #     self._exec_cli(output_path)
        pass

    def _save_hdf5_clicked(self):
        """
        Save HDF5 menu button callback.
        """
    #     if self.video_path:
    #         self._save_hdf5(dialog=True)
        pass

    def _save_hdf5(self, dialog=True):
        """ Saves an HDF5.  Guesses output path if no dialog requested. """
        if dialog:
            output_path = str(QtGui.QFileDialog.getSaveFileName(self,
                              "Save HDF5 as",
                              VIDEO_DIR,
                              filter="HDF5 (*.h5 *.hdf5)"))
        else:
            filename, ext = os.path.splitext(self.video_path)
            output_path = "%s-output.h5" % (filename)

        if output_path:
            self._exec_cli(output_path)

    def _exec_cli(self, output_path):
        """
        Executes CLI process to analyze current movie in full using the
            specified output path.
        """
        if self.custom_algorithm:
            custom = " -a %s" % self.custom_algorithm
        else:
            custom = ""

        eyetracker_path = os.path.join(CURR_DIR, 'eyetracker.py')
        exec_str = "{} {} {} {} -c {}{}{}".format(COMMAND_PREFIX,
                                                  eyetracker_path,
                                                  self.video_path,
                                                  output_path,
                                                  self.config_path,
                                                  custom,
                                                  COMMAND_SUFFIX)

        os.system(exec_str)


        # msg = raw_input('Do you want to excute the following command?\n\n{}\n\n(y/n)\n'.format(exec_str))
        #
        # while True:
        #     if msg == 'y':
        #         is_save = True
        #         break
        #     elif msg == 'n':
        #         is_save = False
        #         print('continue without saving.')
        #         break
        #         # sys.exit('Stop process without saving.')
        #     else:
        #         msg = raw_input('\nDo you want to excute the following command?\n\n{}\n\n(y/n)\n'.format(exec_str))

        # if is_save:
        #     os.system(exec_str)

    def _save_tiff_clicked(self):
        """
        Save tiff stack menu button clicked.
        """
        pass



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = EyetrackerGui()
    myapp.show()
    sys.exit(app.exec_())
