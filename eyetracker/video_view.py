'''
Created on Oct 18, 2012

@author: derricw

Video view for the eyetracker viewer app.

'''

import sys
import os
import time
import numpy as np
import pyqtgraph as pg
from PyQt4 import QtCore, QtGui

from video_layout import Ui_Form


class VideoView(QtGui.QDialog):
    """
    Video view with two roi's that can be repositioned.
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.dataset = None
        self.img_shape = None

        self.index = None

        self.image_count = 0

        self._setupButtons()

        self._setupGraphics()

        self._setupROIs()

    def _setupButtons(self):
        """ Setup button callbacks. """
        pass

    def _setupGraphics(self):
        """ Sets up the graphics. """
        self.img_view = self.ui.graphicsView_img.addViewBox()
        self.img_view.setAspectLocked(True)
        self.img_view.enableAutoRange(True)
        self.img = pg.ImageItem()
        self.img_view.addItem(self.img)
        self.img.scene().sigMouseMoved.connect(self.set_pixel_value)

    def _setupROIs(self):
        """ Sets up the ROI's """
        self.pupil_roi = pg.ROI([50, 50], [50, 50],
                                pen=(0, 255, 0),
                                removable=False)
        self.pupil_roi.addScaleHandle([0, 0.5], [0.5, 0.5])
        self.pupil_roi.addScaleHandle([1, 0.5], [0.5, 0.5])
        self.pupil_roi.addScaleHandle([0.5, 0], [0.5, 0.5])
        self.pupil_roi.addScaleHandle([0.5, 1], [0.5, 0.5])
        self.img_view.addItem(self.pupil_roi)

        self.led_roi = pg.ROI([100, 50], [30, 30],
                              pen=(255, 0, 0),
                              removable=False)
        self.led_roi.addScaleHandle([0, 0.5], [0.5, 0.5])
        self.led_roi.addScaleHandle([1, 0.5], [0.5, 0.5])
        self.led_roi.addScaleHandle([0.5, 0], [0.5, 0.5])
        self.led_roi.addScaleHandle([0.5, 1], [0.5, 0.5])
        self.img_view.addItem(self.led_roi)

    def set_roi_geometry(self, led_roi=None, pupil_roi=None):
        ## CURRENTLY Y IS REVERSED AND I NEED TO FIGURE OUT HOW TO FIX THAT
        if led_roi:
            pos = (led_roi[0], led_roi[1])
            size = (led_roi[2]-led_roi[0], led_roi[3]-led_roi[1])
            self.led_roi.setPos(pos)
            self.led_roi.setSize(size)
        if pupil_roi:
            pos = (pupil_roi[0], pupil_roi[1])
            size = (pupil_roi[2]-pupil_roi[0], pupil_roi[3]-pupil_roi[1])
            self.pupil_roi.setPos(pos)
            self.pupil_roi.setSize(size)

    def set_frame_shape(self, shape):
        self.ui.label_frame_shape.setText(str(shape))

    def set_pixel_value(self, event):
        """ Updates GUI with current cursor position """
        point = self.img_view.mapSceneToView(event)
        x, y = int(point.x()), int(point.y())
        try:
            i = self.img.image[x, y]
        except:
            i = "*"
        self.ui.label_pixel_value.setText("(%i,%i), %s" % (x, y, i))

    def set_image_format(self, shape):
        self.ui.label_frame_shape.setText(str(shape)+" uint8")

    def keyPressEvent(self, e):
        """ Callback for key press event.  Just passes it on to parent. """
        print(e)

    def closeEvent(self, evnt):
        """ Callback for close event. """
        pass
