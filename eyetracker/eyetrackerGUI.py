import sys
from PyQt5 import QtCore, QtGui
from mainwindow_layout import Ui_MainWindow

class EyetrackerGui(QtGui.QMainWindow):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = EyetrackerGui()
    myapp.show()
    sys.exit(app.exec_())