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

from plot_layout import Ui_Form


class PlotView(QtGui.QDialog):
    """
    View for 3 plots with scolling data.
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self._setupButtons()

        self._setupGraphics()

        self._led_pos = None
        self._pupil_pos = None
        self._area = None

        self.x = np.ones(1000)
        self.y = np.ones(1000)
        self.a = np.ones(1000)

        self._p_init = False
        self._a_init = False

    def _setupButtons(self):
        """ Setup button callbacks. """
        pass

    def _setupGraphics(self):
        """ Sets up the graphics. """
        self.x_plot = self.ui.graphicsView.addPlot(row=1, col=0).plot()
        self.y_plot = self.ui.graphicsView.addPlot(row=2, col=0).plot()
        self.a_plot = self.ui.graphicsView.addPlot(row=3, col=0).plot()

        #LABELS? do we need them?

    def addFrame(self, led_pos=None, pupil_pos=None, pupil_area=None):
        """
        Adds one frame worth of data to the plots.
        """
        self._update_pupil(pupil_pos)
        self._update_area(pupil_area)
        self._update_plots()

    def _update_pupil(self, pos):
        """
        Updates the pupil data
        """
        if pos:
            #new position
            if self._p_init:
                #initialized
                self.x[0] = pos[0]
                self.y[0] = pos[1]
            else:
                #not initialized
                self.x = self.x*pos[0]
                self.y = self.y*pos[1]
                self._p_init = True
            self._pupil_pos = pos
            
        else:
            #no new position
            if self._pupil_pos:
                #use last position
                self.x[0] = self._pupil_pos[0]
                self.y[0] = self._pupil_pos[1]
            else:
                #whatever
                pass

        self.x = np.roll(self.x, -1)
        self.y = np.roll(self.y, -1)

    def _update_area(self, area):
        """
        Updates the area data
        """
        if area:
            if self._a_init:
                self.a[0] = area
            else:
                self.a = self.a*area
                self._a_init = True
        else:
            if self._area:
                self.a[0] = self._area
            else:
                pass

        self.a = np.roll(self.a, -1)

    def _update_plots(self):
        """
        Updates the plots
        """
        self.x_plot.setData(y=self.x)
        self.y_plot.setData(y=self.y)
        self.a_plot.setData(y=self.a)

    def keyPressEvent(self, e):
        """ Callback for key press event.  Just passes it on to parent. """
        print(e)

    def closeEvent(self, evnt):
        """ Callback for close event. """
        pass
