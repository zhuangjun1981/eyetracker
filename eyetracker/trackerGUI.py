import os
import sys
import cv2
import numpy as np
import eyetracker.detector as dt
import eyetracker.mainwindow_layout as mwl
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import yaml
import matplotlib.pyplot as plt

PACKAGE_DIR = os.path.dirname(os.path.realpath(__file__))

class EyetrackerGui(QtWidgets.QMainWindow):

    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self, parent)
        self.ui = mwl.Ui_MainWindow()
        self.ui.setupUi(self)

        # setup_graphics
        self.movie_view = self.ui.graphicsView_movieView.addViewBox()
        self.movie_view.setAspectLocked(True)
        self.movie_view.enableAutoRange(True)
        self.movie = pg.ImageItem()
        self.movie_view.addItem(self.movie)
        self.movie_timer = QtCore.QTimer(self.movie)


        self.clear()

        self.pupil_roi.sigRegionChanged.connect(self._update_parameters)
        self.led_roi.sigRegionChanged.connect(self._update_parameters)
        self.ui.lineEdit_ledBlur.textChanged.connect(self._update_parameters)
        self.ui.lineEdit_ledBinary.textChanged.connect(self._update_parameters)
        self.ui.lineEdit_ledOpenClose.textChanged.connect(self._update_parameters)
        self.ui.lineEdit_ledMinSize.textChanged.connect(self._update_parameters)
        self.ui.lineEdit_ledMaxSize.textChanged.connect(self._update_parameters)
        self.ui.lineEdit_ledMaskDilation.textChanged.connect(self._update_parameters)
        self.ui.checkBox_pupilEqualize.stateChanged.connect(self._update_parameters)
        self.ui.lineEdit_pupilBlur.textChanged.connect(self._update_parameters)
        self.ui.lineEdit_pupilBinary.textChanged.connect(self._update_parameters)
        self.ui.lineEdit_pupilOpenClose.textChanged.connect(self._update_parameters)
        self.ui.lineEdit_pupilMinSize.textChanged.connect(self._update_parameters)

        self.ui.horizontalSlider_currentFrame.valueChanged.connect(self._slider_value_changed)
        # self.ui.lineEdit_currframeNum.textChanged.connect(self._frame_ind_specified)
        self.ui.lineEdit_currframeNum.returnPressed.connect(self._frame_ind_specified)

        self.ui.pushButton_loadMovie.clicked.connect(self.load_movie)
        self.ui.pushButton_clear.clicked.connect(self.clear)

        self.ui.pushButton_pauseplay.clicked.connect(self._playpause_clicked)
        self.ui.pushButton_loadConfig.clicked.connect(self._load_config_clicked)
        self.ui.pushButton_saveConfig.clicked.connect(self._save_config_clicked)
        self.ui.pushButton_showResult.clicked.connect(self._show_result_clicked)
        self.ui.pushButton_process.clicked.connect(self._process_clicked)

        self.movie_timer.timeout.connect(self._show_next_frame)

        # 0: no movie loaded
        # 1: movie loaded and paused
        # 2: movie loaded and running
        # self.status = 0

    def clear(self):

        # print('self.clear()')

        if hasattr(self, 'status') and self.status == 2: # if movie is playing
            self._pause_movie()

        # set slider
        self.ui.horizontalSlider_currentFrame.setRange(0, 1)
        self.ui.horizontalSlider_currentFrame.setValue(0)
        self.ui.horizontalSlider_currentFrame.setEnabled(False)

        # set current frame
        self.ui.lineEdit_currframeNum.setText('0')
        self.ui.lineEdit_currframeNum.setEnabled(False)

        # setup pupil and led rois
        if hasattr(self, 'pupil_roi'):
            self.pupil_roi.setPos((20, 20))
            self.pupil_roi.setSize((60, 60))
            self.pupil_roi.setPen((0, 255, 0))
            self.pupil_roi.removable = False
        else:
            self.pupil_roi = pg.ROI([20, 20], [60, 60],
                                    pen=(0, 255, 0),
                                    removable=False)
            self.pupil_roi.handleSize = 10
            self.pupil_roi.addScaleHandle([1, 0], [0, 1])
            self.pupil_roi.addScaleHandle([0, 0], [1, 1])
            self.pupil_roi.addScaleHandle([1, 1], [0, 0])
            self.pupil_roi.addScaleHandle([0, 1], [1, 0])
            self.movie_view.addItem(self.pupil_roi)

        if hasattr(self, 'led_roi'):
            self.led_roi.setPos((40, 40))
            self.led_roi.setSize((20, 20))
            self.led_roi.setPen((255, 0, 0))
            self.led_roi.removable = False
        else:
            self.led_roi = pg.ROI([40, 40], [20, 20],
                                  pen=(255, 0, 0),
                                  removable=False, )
            self.led_roi.handleSize = 10
            self.led_roi.addScaleHandle([1, 0], [0, 1])
            self.led_roi.addScaleHandle([0, 0], [1, 1])
            self.led_roi.addScaleHandle([1, 1], [0, 0])
            self.led_roi.addScaleHandle([0, 1], [1, 0])
            self.movie_view.addItem(self.led_roi)

        # set background image
        # print('resetting image')
        self.movie.setImage(np.zeros((100, 100), dtype=np.uint8))

        # setup movie properties
        self.video_capture = None
        self.movie_path = None
        self.movie_frame_num = 0
        self.movie_frame_shape = (100, 100) # (height, width)
        self.movie_fps = None
        self.curr_frame_ind = None
        self.last_pupil=(None, None) # (frame ind, pupil Ellipse)
        self._show_movie_info()

        # set buttons
        self.ui.pushButton_pauseplay.setIcon(QtGui.QIcon(os.path.join(PACKAGE_DIR, "res", "play.png")))
        self.ui.pushButton_pauseplay.setEnabled(False)
        self.ui.pushButton_saveConfig.setEnabled(False)
        self.ui.pushButton_showResult.setEnabled(False)
        self.ui.pushButton_process.setEnabled(False)

        # initiated detector
        self.detector = dt.PupilLedDetector(led_roi=self._qt_roi_2_detector_roi(self.led_roi),
                                            pupil_roi=self._qt_roi_2_detector_roi(self.pupil_roi))
        self._show_detector_parameters()

        # remove result
        self.ui.textBrowser_results.setText('')

        self.status = 0

    def load_movie(self):

        print('loading movie')

        if self.movie_path is not None:
            last_dir = os.path.dirname(self.movie_path)
        else:
            last_dir = os.path.join(PACKAGE_DIR, 'tests', 'test_files')


        movie_path = QtWidgets.QFileDialog.getOpenFileName(self, caption="select a input .avi movie file",
                                                           directory=last_dir,
                                                           filter='*.avi')[0]

        if movie_path:

            video_capture = cv2.VideoCapture(movie_path)
            frame_num = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

            if frame_num > 0:
                self.movie_path = os.path.realpath(movie_path)
                self.video_capture = video_capture
                self.movie_frame_num = frame_num
                self.movie_frame_shape = (int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                                          int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)))
                self.movie_fps = self.video_capture.get(cv2.CAP_PROP_FPS)

                self.ui.horizontalSlider_currentFrame.setRange(0, self.movie_frame_num - 1)

                # display info
                self._show_movie_info()

                # try to load config file
                self._load_config_clicked()

                # set up status
                self.status = 1
                self._pause_movie()

                # display frame
                self.curr_frame_ind = 0
                self._show_one_frame(frame_ind=self.curr_frame_ind)
                self.last_pupil = (0, self.detector.pupil)

            else: # no frame in the movie
                print('\nno frame in the selected movie file: \n{}'.format(self.movie_path))

    def _slider_value_changed(self):

        # print('slider bar value changed')

        self.curr_frame_ind = int(self.ui.horizontalSlider_currentFrame.value())
        self._show_one_frame(frame_ind=self.curr_frame_ind)

    def _frame_ind_specified(self):

        # print('frame index specified.')

        def go_back():
            self.ui.lineEdit_currframeNum.blockSignals(True)
            self.ui.lineEdit_currframeNum.setText(str(self.curr_frame_ind))
            self.ui.lineEdit_currframeNum.blockSignals(False)

        try:
            frame_i = int(self.ui.lineEdit_currframeNum.text())
        except ValueError:
            go_back()
            print('input frame number should be a unsigned integer.')
            return

        if frame_i < 0:
            print('input frame index should be a unsigned integer.')
            go_back()
        elif frame_i >= self.movie_frame_num:
            print('input frame index ({}) should be less than total frame number ({}).'
                  .format(frame_i, self.movie_frame_num))
            go_back()
        elif frame_i == self.curr_frame_ind:
            return
        else:
            self.curr_frame_ind = frame_i
            self._show_one_frame(frame_ind=self.curr_frame_ind)

    def _playpause_clicked(self):

        print('play/paused clicked')

        if self.status == 0:
            print('no movie loaded. Cannot play or pause movie.')
        elif self.status == 1:
            self._play_movie()
        elif self.status == 2:
            self._pause_movie()
        else:
            print('do not understand internal status: {}. Do nothing.'.format(self.status))

    def _load_config_clicked(self):

        # print('self._load_config_clicked()')

        if self.movie_path is None:
            # self.led_roi.setPos((40, 40))
            # self.led_roi.setSize((20, 20))
            # self.pupil_roi.setPos((20, 20))
            # self.pupil_roi.setSize((60, 60))
            print('self.movie_path is None. Cannot load config file.')

        else:
            if (self.config_path is not None) and (os.path.isfile(self.config_path)):
                print('\nloading existing config file: \n{}'.format(self.config_path))
                with open(self.config_path, 'r') as config_f:
                    param_dict = yaml.load(config_f)
            else:
                print('\ncannnot find existing config file. load the default detector parameters.')
                detector = dt.PupilLedDetector()
                param_dict = detector.get_parameter_dict()

            if param_dict['led_roi'] is None:
                self.led_roi.setPos((0, 0))
                self.led_roi.setSize((self.movie_frame_shape[1], self.movie_frame_shape[0]))
                param_dict['led_roi'] = self._qt_roi_2_detector_roi(self.led_roi)
            else:
                led_roi_pos, led_roi_size = self._detector_roi_2_qt_roi(param_dict['led_roi'])
                self.led_roi.setPos(led_roi_pos)
                self.led_roi.setSize(led_roi_size)

            if param_dict['pupil_roi'] is None:
                self.pupil_roi.setPos((0, 0))
                self.pupil_roi.setSize((self.movie_frame_shape[1], self.movie_frame_shape[0]))
                param_dict['pupil_roi'] = self._qt_roi_2_detector_roi(self.pupil_roi)
            else:
                pupil_roi_pos, pupil_roi_size = self._detector_roi_2_qt_roi(param_dict['pupil_roi'])
                self.pupil_roi.setPos(pupil_roi_pos)
                self.pupil_roi.setSize(pupil_roi_size)

            self.detector.load_parameters(**param_dict)
            self._show_detector_parameters()
            print(self.detector.param_str)

    def _save_config_clicked(self):
        if self.status == 0:
            print('no movie loaded. Can not save config file.')
        else:
            if (self.config_path is not None) and (os.path.isfile(self.config_path)):
                print('Overwriting existing config file: \n{}'.format(self.config_path))
                os.remove(self.config_path)

            self._update_parameters()
            with open(self.config_path, 'w') as config_f:
                yaml.dump(self.detector.get_parameter_dict(), config_f)

    def _show_result_clicked(self):
        self.detector.show_results()
        plt.show()

    def _process_clicked(self):

        if self.status == 0:
            print('No movie loaded. Cannot process.')
        else:
            self._save_config_clicked()
            python_path = sys.executable
            tracker_path = os.path.join(PACKAGE_DIR, 'tracker.py')
            movie_path = self.movie_path
            config_path = self.config_path
            cmd = "start {} {} {} -c {}".format(python_path,
                                                tracker_path,
                                                movie_path,
                                                config_path)
            os.system(cmd)

    def _update_parameters(self):

        led_roi = self._qt_roi_2_detector_roi(self.led_roi)
        pupil_roi = self._qt_roi_2_detector_roi(self.pupil_roi)

        self.detector.load_parameters(led_roi=led_roi,
                                      led_blur=int(self.ui.lineEdit_ledBlur.text()),
                                      led_binary_threshold=int(self.ui.lineEdit_ledBinary.text()),
                                      led_openclose_iter=int(self.ui.lineEdit_ledOpenClose.text()),
                                      led_min_size=float(self.ui.lineEdit_ledMinSize.text()),
                                      led_max_size=float(self.ui.lineEdit_ledMaxSize.text()),
                                      led_mask_dilation=int(self.ui.lineEdit_ledMaskDilation.text()),
                                      pupil_is_equalize=self.ui.checkBox_pupilEqualize.isChecked(),
                                      pupil_roi=pupil_roi,
                                      pupil_blur=int(self.ui.lineEdit_pupilBlur.text()),
                                      pupil_binary_threshold=int(self.ui.lineEdit_pupilBinary.text()),
                                      pupil_openclose_iter=int(self.ui.lineEdit_pupilOpenClose.text()),
                                      pupil_min_size=float(self.ui.lineEdit_pupilMinSize.text()))

        self._show_detector_parameters()

        if self.status == 1:
            self._show_one_frame(frame_ind=self.curr_frame_ind)

    def _play_movie(self):

        if self.status == 0:
            print('no movie loaded. Cannot play movie.')
        elif self.status == 2:
            return
        elif self.status == 1:

            # set frame slider
            self.ui.horizontalSlider_currentFrame.setEnabled(False)

            # set frame lineEdit
            self.ui.lineEdit_currframeNum.setEnabled(False)

            # set buttons
            self.ui.pushButton_pauseplay.setEnabled(True)
            self.ui.pushButton_pauseplay.setIcon(QtGui.QIcon(os.path.join(PACKAGE_DIR, "res", "pause.png")))
            self.ui.pushButton_showResult.setEnabled(False)
            self.ui.pushButton_process.setEnabled(False)

            # change status
            self.status = 2

            self.movie_timer.start(int(1 / self.movie_fps))

        else:
            print('do not understand internal status ({}). Do nothing.'.format(self.status))

    def _pause_movie(self):

        if self.status == 0:
            print('no movie loaded. Cannot pause movie.')
        else:

            self.movie_timer.stop()

            # set frame slider
            self.ui.horizontalSlider_currentFrame.setEnabled(True)

            # set frame lineEdit
            self.ui.lineEdit_currframeNum.setEnabled(True)

            # set buttons
            self.ui.pushButton_pauseplay.setEnabled(True)
            self.ui.pushButton_pauseplay.setIcon(QtGui.QIcon(os.path.join(PACKAGE_DIR, "res", "play.png")))
            self.ui.pushButton_saveConfig.setEnabled(True)
            self.ui.pushButton_showResult.setEnabled(True)
            self.ui.pushButton_process.setEnabled(True)

            # change status
            self.status = 1

            print('movie paused.')

    def _show_one_frame(self, frame_ind=None):

        # print('showing one frame')

        if frame_ind is None:
            frame_ind = self.curr_frame_ind
            print(frame_ind)

        if self.status == 0:
            print('No movie loaded. Cannot show frame.')
        elif frame_ind < 0:
            print('frame index ({}) should be non-negative.'.format(frame_ind))
            return
        elif self.movie_frame_num != 0 and frame_ind >= self.movie_frame_num:
            print('frame index ({}) outside of movie frame range (0, {}).'.format(frame_ind, self.movie_frame_num))
            return
        else:

            # setup display without triggering detection
            self.ui.horizontalSlider_currentFrame.blockSignals(True)
            self.ui.lineEdit_currframeNum.blockSignals(True)
            self.ui.horizontalSlider_currentFrame.setValue(frame_ind)
            self.ui.lineEdit_currframeNum.setText(str(frame_ind))
            self.ui.horizontalSlider_currentFrame.blockSignals(False)
            self.ui.lineEdit_currframeNum.blockSignals(False)

            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_ind)
            _, curr_frame = self.video_capture.read()
            self.detector.load_frame(frame=curr_frame)


            if self.last_pupil[0] is None:
                # print('frame index: {}, detect without history.'.format(frame_ind))
                self.detector.detect(last_pupil=None)
            else:
                if frame_ind - self.last_pupil[0] == 1:
                    # print('frame index: {}, detect with history.'.format(frame_ind))
                    self.detector.detect(last_pupil=self.last_pupil[1])
                else:
                    # print('frame index: {}, detect without history.'.format(frame_ind))
                    self.detector.detect(last_pupil=None)

            # not sure if this check is a good or bad thing
            # if self.detector.pupil is not None:
            #     self.last_pupil = (frame_ind, self.detector.pupil)

            self.last_pupil = (frame_ind, self.detector.pupil)
            self._show_image(self.detector.annotated)

            # show result text
            self.ui.textBrowser_results.setText(self.detector.result_str)

    def _show_next_frame(self):

        self.curr_frame_ind = (self.curr_frame_ind + 1) % self.movie_frame_num

        # print("trackerGUI showing next frame: {}".format(self.curr_frame_ind))

        self._show_one_frame(frame_ind=self.curr_frame_ind)

    def _qt_roi_2_detector_roi(self, qt_roi):

        top = self.movie_frame_shape[0] - (qt_roi.pos()[1] + qt_roi.size()[1])
        bottom = top + qt_roi.size()[1]
        left = qt_roi.pos()[0]
        right = left + qt_roi.size()[0]

        return (int(top), int(bottom), int(left), int(right))

    def _detector_roi_2_qt_roi(self, detector_roi):

        pos = (detector_roi[2], self.movie_frame_shape[0] - detector_roi[1])
        size = (detector_roi[3] - detector_roi[2], detector_roi[1] - detector_roi[0])

        return pos, size

    def _show_image(self, img):

        img_to_show = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.movie.setImage(cv2.flip(cv2.transpose(img_to_show), 1))

    def _show_movie_info(self):

        self.ui.label_moviePathValue.setText(str(self.movie_path))
        self.ui.label_movieFrameNumberValue.setText(str(self.movie_frame_num))
        self.ui.label_movieFrameShapeValue.setText(str(self.movie_frame_shape))

    def _show_detector_parameters(self):

        # print('self._show_detector_parameters()')

        self._block_param_line_edit_signal()

        self.ui.label_ledROIValue.setText(str(self.detector.led_roi))
        self.ui.lineEdit_ledBlur.setText(str(self.detector.led_blur))
        self.ui.lineEdit_ledBinary.setText(str(self.detector.led_binary_thresh))
        self.ui.lineEdit_ledOpenClose.setText(str(self.detector.led_openclose_iter))
        self.ui.lineEdit_ledMinSize.setText('{:8.2f}'.format(self.detector.led_min_size))
        self.ui.lineEdit_ledMaxSize.setText('{:8.2f}'.format(self.detector.led_max_size))
        self.ui.lineEdit_ledMaskDilation.setText(str(self.detector.led_mask_dilation))

        self.ui.checkBox_pupilEqualize.setChecked(self.detector.pupil_is_equalize)
        self.ui.label_pupilROIValue.setText(str(self.detector.pupil_roi))
        self.ui.lineEdit_pupilBlur.setText(str(self.detector.pupil_blur))
        self.ui.lineEdit_pupilBinary.setText(str(self.detector.pupil_binary_thresh))
        self.ui.lineEdit_pupilOpenClose.setText(str(self.detector.pupil_openclose_iter))
        self.ui.lineEdit_pupilMinSize.setText('{:8.2f}'.format(self.detector.pupil_min_size))

        self._enable_params_line_edit_signal()

    def _block_param_line_edit_signal(self):

        # print('self._block_param_line_edit_signal()')

        self.ui.lineEdit_ledBlur.blockSignals(True)
        self.ui.lineEdit_ledBinary.blockSignals(True)
        self.ui.lineEdit_ledOpenClose.blockSignals(True)
        self.ui.lineEdit_ledMinSize.blockSignals(True)
        self.ui.lineEdit_ledMaxSize.blockSignals(True)
        self.ui.lineEdit_ledMaskDilation.blockSignals(True)

        self.ui.checkBox_pupilEqualize.blockSignals(True)
        self.ui.lineEdit_pupilBlur.blockSignals(True)
        self.ui.lineEdit_pupilBinary.blockSignals(True)
        self.ui.lineEdit_pupilOpenClose.blockSignals(True)
        self.ui.lineEdit_pupilMinSize.blockSignals(True)

    def _enable_params_line_edit_signal(self):

        # print('self._enable_params_line_edit_signal()')

        self.ui.lineEdit_ledBlur.blockSignals(False)
        self.ui.lineEdit_ledBinary.blockSignals(False)
        self.ui.lineEdit_ledOpenClose.blockSignals(False)
        self.ui.lineEdit_ledMinSize.blockSignals(False)
        self.ui.lineEdit_ledMaxSize.blockSignals(False)
        self.ui.lineEdit_ledMaskDilation.blockSignals(False)

        self.ui.checkBox_pupilEqualize.blockSignals(False)
        self.ui.lineEdit_pupilBlur.blockSignals(False)
        self.ui.lineEdit_pupilBinary.blockSignals(False)
        self.ui.lineEdit_pupilOpenClose.blockSignals(False)
        self.ui.lineEdit_pupilMinSize.blockSignals(False)


    @property
    def config_path(self):

        if self.movie_path is not None:
            return os.path.splitext(self.movie_path)[0] + '_output.yml'
        else:
            return None


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = EyetrackerGui()
    myapp.show()
    sys.exit(app.exec_())