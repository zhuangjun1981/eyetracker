import sys
import cv2
import numpy as np
import eyetracker.detector as dt
import eyetracker.mainwindow_layout as mwl
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

class EyetrackerGui(QtWidgets.QMainWindow):

    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self, parent)
        self.ui = mwl.Ui_MainWindow()
        self.ui.setupUi(self)

        # setup_graphics
        self.movie_view = self.ui.graphicsView_img.addViewBox()
        self.movie_view.setAspectLocked(True)
        self.movie_view.enableAutoRange(True)
        self.movie = pg.ImageItem()
        self.movie_view.addItem(self.movie)


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

        self.ui.pushButton_loadMovie.clicked.connect(self._load_movie_clicked)

        # 0: no movie loaded
        # 1: movie loaded and paused
        # 2: movie loaded and running
        # self.status = 0


    def clear(self):

        # setup pupil and led rois
        self.pupil_roi = pg.ROI([20, 20], [60, 60],
                                pen=(0, 255, 0),
                                removable=False)
        self.pupil_roi.addScaleHandle([0, 0.5], [0.5, 0.5])
        self.pupil_roi.addScaleHandle([1, 0.5], [0.5, 0.5])
        self.pupil_roi.addScaleHandle([0.5, 0], [0.5, 0.5])
        self.pupil_roi.addScaleHandle([0.5, 1], [0.5, 0.5])
        self.movie_view.addItem(self.pupil_roi)

        self.led_roi = pg.ROI([40, 40], [20, 20],
                              pen=(255, 0, 0),
                              removable=False)
        self.led_roi.addScaleHandle([0, 0.5], [0.5, 0.5])
        self.led_roi.addScaleHandle([1, 0.5], [0.5, 0.5])
        self.led_roi.addScaleHandle([0.5, 0], [0.5, 0.5])
        self.led_roi.addScaleHandle([0.5, 1], [0.5, 0.5])
        self.movie_view.addItem(self.led_roi)

        # set back image
        self.movie.setImage(np.zeros((100, 100), dtype=np.uint8))

        # setup movie properties
        self.video_capture = None
        self.movie_path = None
        self.movie_frame_num = 0
        self.movie_frame_shape = (100, 100) # (height, width)

        # initiated detector
        self.detector = dt.PupilLedDetector(led_roi=self._qt_roi_2_detector_roi(self.led_roi),
                                            pupil_roi=self._qt_roi_2_detector_roi(self.pupil_roi))
        self._show_detector_parameters()

        self.status = 0

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

    def _show_movie_info(self):

        self.ui.label_moviePathValue.setText(str(self.movie_path))
        self.ui.label_movieFrameNumber.setText(str(self.movie_frame_num))
        self.ui.label_movieFrameShape.setText(str(self.movie_frame_shape))

    def _show_detector_parameters(self):

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

    def _load_movie_clicked(self):
        pass

    def _playpause_clicked(self):
        pass

    def _show_result_clicked(self):
        pass

    def _save_config_clicked(self):
        pass

    def _load_config_clicked(self):
        pass

    def _qt_roi_2_detector_roi(self, qt_roi):

        top = self.movie_frame_shape[0] - (qt_roi.pos()[1] + qt_roi.size()[1])
        bottom = top + qt_roi.size()[1]
        left = qt_roi.pos()[0]
        right = left + qt_roi.size()[0]

        return (int(top), int(bottom), int(left), int(right))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = EyetrackerGui()
    myapp.show()
    sys.exit(app.exec_())