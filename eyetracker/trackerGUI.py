import sys
import cv2
import eyetracker.detector as dt
import eyetracker.mainwindow_layout as mwl
from PyQt5 import QtCore, QtGui, QtWidgets

class EyetrackerGui(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = mwl.Ui_MainWindow()
        self.ui.setupUi(self)

        self.detector = dt.PupilLedDetector(led_roi=None,
                                            pupil_roi=None)

    def load_movie(self):
        pass

    def play(self):
        pass

    def pause(self):
        pass

    def save_config(self):
        pass

    def load_config(self):
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = EyetrackerGui()
    myapp.show()
    sys.exit(app.exec_())