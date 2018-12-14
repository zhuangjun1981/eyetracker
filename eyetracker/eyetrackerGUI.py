import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from mainwindow_layout import Ui_MainWindow

class EyetrackerGui(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = EyetrackerGui()
    myapp.show()
    sys.exit(app.exec_())