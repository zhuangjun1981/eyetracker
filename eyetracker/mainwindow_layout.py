# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1004, 685)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("res/eye.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox_pupil = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_pupil.setGeometry(QtCore.QRect(750, 240, 241, 171))
        self.groupBox_pupil.setObjectName("groupBox_pupil")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox_pupil)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_pupilBinary = QtWidgets.QLabel(self.groupBox_pupil)
        self.label_pupilBinary.setObjectName("label_pupilBinary")
        self.gridLayout_5.addWidget(self.label_pupilBinary, 4, 0, 1, 1)
        self.label_pupilMinSize = QtWidgets.QLabel(self.groupBox_pupil)
        self.label_pupilMinSize.setObjectName("label_pupilMinSize")
        self.gridLayout_5.addWidget(self.label_pupilMinSize, 6, 0, 1, 1)
        self.label_pupilROI = QtWidgets.QLabel(self.groupBox_pupil)
        self.label_pupilROI.setObjectName("label_pupilROI")
        self.gridLayout_5.addWidget(self.label_pupilROI, 1, 0, 1, 1)
        self.lineEdit_pupilBinary = QtWidgets.QLineEdit(self.groupBox_pupil)
        self.lineEdit_pupilBinary.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_pupilBinary.setObjectName("lineEdit_pupilBinary")
        self.gridLayout_5.addWidget(self.lineEdit_pupilBinary, 4, 1, 1, 1)
        self.lineEdit_pupilOpenClose = QtWidgets.QLineEdit(self.groupBox_pupil)
        self.lineEdit_pupilOpenClose.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_pupilOpenClose.setObjectName("lineEdit_pupilOpenClose")
        self.gridLayout_5.addWidget(self.lineEdit_pupilOpenClose, 5, 1, 1, 1)
        self.label_pupilBlur = QtWidgets.QLabel(self.groupBox_pupil)
        self.label_pupilBlur.setObjectName("label_pupilBlur")
        self.gridLayout_5.addWidget(self.label_pupilBlur, 3, 0, 1, 1)
        self.label_pupilOpenClose = QtWidgets.QLabel(self.groupBox_pupil)
        self.label_pupilOpenClose.setObjectName("label_pupilOpenClose")
        self.gridLayout_5.addWidget(self.label_pupilOpenClose, 5, 0, 1, 1)
        self.lineEdit_pupilBlur = QtWidgets.QLineEdit(self.groupBox_pupil)
        self.lineEdit_pupilBlur.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_pupilBlur.setObjectName("lineEdit_pupilBlur")
        self.gridLayout_5.addWidget(self.lineEdit_pupilBlur, 3, 1, 1, 1)
        self.label_pupilEqualize = QtWidgets.QLabel(self.groupBox_pupil)
        self.label_pupilEqualize.setObjectName("label_pupilEqualize")
        self.gridLayout_5.addWidget(self.label_pupilEqualize, 0, 0, 1, 1)
        self.checkBox_pupilEqualize = QtWidgets.QCheckBox(self.groupBox_pupil)
        self.checkBox_pupilEqualize.setText("")
        self.checkBox_pupilEqualize.setChecked(False)
        self.checkBox_pupilEqualize.setObjectName("checkBox_pupilEqualize")
        self.gridLayout_5.addWidget(self.checkBox_pupilEqualize, 0, 1, 1, 1)
        self.lineEdit_pupilMinSize = QtWidgets.QLineEdit(self.groupBox_pupil)
        self.lineEdit_pupilMinSize.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_pupilMinSize.setObjectName("lineEdit_pupilMinSize")
        self.gridLayout_5.addWidget(self.lineEdit_pupilMinSize, 6, 1, 1, 1)
        self.label_pupilROIValue = QtWidgets.QLabel(self.groupBox_pupil)
        self.label_pupilROIValue.setObjectName("label_pupilROIValue")
        self.gridLayout_5.addWidget(self.label_pupilROIValue, 1, 1, 1, 1)
        self.groupBox_led = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_led.setGeometry(QtCore.QRect(750, 20, 241, 201))
        self.groupBox_led.setObjectName("groupBox_led")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_led)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_ledBlur = QtWidgets.QLabel(self.groupBox_led)
        self.label_ledBlur.setObjectName("label_ledBlur")
        self.gridLayout_4.addWidget(self.label_ledBlur, 1, 0, 1, 1)
        self.label_ledOpenClose = QtWidgets.QLabel(self.groupBox_led)
        self.label_ledOpenClose.setObjectName("label_ledOpenClose")
        self.gridLayout_4.addWidget(self.label_ledOpenClose, 3, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox_led)
        self.label.setObjectName("label")
        self.gridLayout_4.addWidget(self.label, 6, 0, 1, 1)
        self.label_ledBinary = QtWidgets.QLabel(self.groupBox_led)
        self.label_ledBinary.setObjectName("label_ledBinary")
        self.gridLayout_4.addWidget(self.label_ledBinary, 2, 0, 1, 1)
        self.label_led_min = QtWidgets.QLabel(self.groupBox_led)
        self.label_led_min.setObjectName("label_led_min")
        self.gridLayout_4.addWidget(self.label_led_min, 4, 0, 1, 1)
        self.label_ledROI = QtWidgets.QLabel(self.groupBox_led)
        self.label_ledROI.setObjectName("label_ledROI")
        self.gridLayout_4.addWidget(self.label_ledROI, 0, 0, 1, 1)
        self.label_ledMaxSize = QtWidgets.QLabel(self.groupBox_led)
        self.label_ledMaxSize.setObjectName("label_ledMaxSize")
        self.gridLayout_4.addWidget(self.label_ledMaxSize, 5, 0, 1, 1)
        self.lineEdit_ledBlur = QtWidgets.QLineEdit(self.groupBox_led)
        self.lineEdit_ledBlur.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_ledBlur.setObjectName("lineEdit_ledBlur")
        self.gridLayout_4.addWidget(self.lineEdit_ledBlur, 1, 1, 1, 1)
        self.lineEdit_ledBinary = QtWidgets.QLineEdit(self.groupBox_led)
        self.lineEdit_ledBinary.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_ledBinary.setObjectName("lineEdit_ledBinary")
        self.gridLayout_4.addWidget(self.lineEdit_ledBinary, 2, 1, 1, 1)
        self.lineEdit_ledOpenClose = QtWidgets.QLineEdit(self.groupBox_led)
        self.lineEdit_ledOpenClose.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_ledOpenClose.setObjectName("lineEdit_ledOpenClose")
        self.gridLayout_4.addWidget(self.lineEdit_ledOpenClose, 3, 1, 1, 1)
        self.lineEdit_ledMinSize = QtWidgets.QLineEdit(self.groupBox_led)
        self.lineEdit_ledMinSize.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_ledMinSize.setObjectName("lineEdit_ledMinSize")
        self.gridLayout_4.addWidget(self.lineEdit_ledMinSize, 4, 1, 1, 1)
        self.lineEdit_ledMaxSize = QtWidgets.QLineEdit(self.groupBox_led)
        self.lineEdit_ledMaxSize.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_ledMaxSize.setObjectName("lineEdit_ledMaxSize")
        self.gridLayout_4.addWidget(self.lineEdit_ledMaxSize, 5, 1, 1, 1)
        self.lineEdit_ledMaskDilation = QtWidgets.QLineEdit(self.groupBox_led)
        self.lineEdit_ledMaskDilation.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_ledMaskDilation.setObjectName("lineEdit_ledMaskDilation")
        self.gridLayout_4.addWidget(self.lineEdit_ledMaskDilation, 6, 1, 1, 1)
        self.label_ledROIValue = QtWidgets.QLabel(self.groupBox_led)
        self.label_ledROIValue.setObjectName("label_ledROIValue")
        self.gridLayout_4.addWidget(self.label_ledROIValue, 0, 1, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(750, 420, 241, 191))
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_10 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.textBrowser_results = QtWidgets.QTextBrowser(self.groupBox_3)
        self.textBrowser_results.setObjectName("textBrowser_results")
        self.gridLayout_10.addWidget(self.textBrowser_results, 1, 0, 1, 1)
        self.horizontalSlider_currentFrame = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider_currentFrame.setEnabled(False)
        self.horizontalSlider_currentFrame.setGeometry(QtCore.QRect(10, 631, 551, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalSlider_currentFrame.sizePolicy().hasHeightForWidth())
        self.horizontalSlider_currentFrame.setSizePolicy(sizePolicy)
        self.horizontalSlider_currentFrame.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_currentFrame.setObjectName("horizontalSlider_currentFrame")
        self.pushButton_pauseplay = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_pauseplay.setEnabled(False)
        self.pushButton_pauseplay.setGeometry(QtCore.QRect(700, 621, 50, 50))
        self.pushButton_pauseplay.setMinimumSize(QtCore.QSize(50, 50))
        self.pushButton_pauseplay.setMaximumSize(QtCore.QSize(50, 50))
        self.pushButton_pauseplay.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("res/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_pauseplay.setIcon(icon1)
        self.pushButton_pauseplay.setIconSize(QtCore.QSize(32, 32))
        self.pushButton_pauseplay.setObjectName("pushButton_pauseplay")
        self.pushButton_saveConfig = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_saveConfig.setGeometry(QtCore.QRect(820, 621, 50, 50))
        self.pushButton_saveConfig.setMinimumSize(QtCore.QSize(50, 50))
        self.pushButton_saveConfig.setMaximumSize(QtCore.QSize(50, 50))
        self.pushButton_saveConfig.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("res/save_config.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_saveConfig.setIcon(icon2)
        self.pushButton_saveConfig.setIconSize(QtCore.QSize(32, 32))
        self.pushButton_saveConfig.setObjectName("pushButton_saveConfig")
        self.pushButton_loadConfig = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_loadConfig.setGeometry(QtCore.QRect(760, 621, 50, 50))
        self.pushButton_loadConfig.setMinimumSize(QtCore.QSize(50, 50))
        self.pushButton_loadConfig.setMaximumSize(QtCore.QSize(50, 50))
        self.pushButton_loadConfig.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("res/load_config.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_loadConfig.setIcon(icon3)
        self.pushButton_loadConfig.setIconSize(QtCore.QSize(32, 32))
        self.pushButton_loadConfig.setObjectName("pushButton_loadConfig")
        self.pushButton_process = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_process.setEnabled(False)
        self.pushButton_process.setGeometry(QtCore.QRect(940, 621, 50, 50))
        self.pushButton_process.setMinimumSize(QtCore.QSize(50, 50))
        self.pushButton_process.setMaximumSize(QtCore.QSize(50, 50))
        self.pushButton_process.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("res/process.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_process.setIcon(icon4)
        self.pushButton_process.setIconSize(QtCore.QSize(32, 32))
        self.pushButton_process.setObjectName("pushButton_process")
        self.pushButton_showResult = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_showResult.setEnabled(False)
        self.pushButton_showResult.setGeometry(QtCore.QRect(880, 621, 51, 51))
        self.pushButton_showResult.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("res/zoom.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_showResult.setIcon(icon5)
        self.pushButton_showResult.setIconSize(QtCore.QSize(32, 32))
        self.pushButton_showResult.setObjectName("pushButton_showResult")
        self.groupBox_movieInfo = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_movieInfo.setGeometry(QtCore.QRect(100, 20, 551, 71))
        self.groupBox_movieInfo.setObjectName("groupBox_movieInfo")
        self.label_moviePath = QtWidgets.QLabel(self.groupBox_movieInfo)
        self.label_moviePath.setGeometry(QtCore.QRect(10, 10, 71, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_moviePath.setFont(font)
        self.label_moviePath.setObjectName("label_moviePath")
        self.label_movieFrameNumber = QtWidgets.QLabel(self.groupBox_movieInfo)
        self.label_movieFrameNumber.setGeometry(QtCore.QRect(10, 40, 131, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_movieFrameNumber.setFont(font)
        self.label_movieFrameNumber.setObjectName("label_movieFrameNumber")
        self.label_moviePathValue = QtWidgets.QLabel(self.groupBox_movieInfo)
        self.label_moviePathValue.setGeometry(QtCore.QRect(70, 10, 471, 31))
        self.label_moviePathValue.setWordWrap(True)
        self.label_moviePathValue.setObjectName("label_moviePathValue")
        self.label_movieFrameNumberValue = QtWidgets.QLabel(self.groupBox_movieInfo)
        self.label_movieFrameNumberValue.setGeometry(QtCore.QRect(140, 40, 111, 20))
        self.label_movieFrameNumberValue.setObjectName("label_movieFrameNumberValue")
        self.label_movieFrameShape = QtWidgets.QLabel(self.groupBox_movieInfo)
        self.label_movieFrameShape.setGeometry(QtCore.QRect(270, 40, 171, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_movieFrameShape.setFont(font)
        self.label_movieFrameShape.setObjectName("label_movieFrameShape")
        self.label_movieFrameShapeValue = QtWidgets.QLabel(self.groupBox_movieInfo)
        self.label_movieFrameShapeValue.setGeometry(QtCore.QRect(450, 40, 91, 20))
        self.label_movieFrameShapeValue.setObjectName("label_movieFrameShapeValue")
        self.lineEdit_currframeNum = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_currframeNum.setEnabled(False)
        self.lineEdit_currframeNum.setGeometry(QtCore.QRect(570, 620, 121, 51))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.lineEdit_currframeNum.setFont(font)
        self.lineEdit_currframeNum.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_currframeNum.setObjectName("lineEdit_currframeNum")
        self.pushButton_loadMovie = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_loadMovie.setEnabled(True)
        self.pushButton_loadMovie.setGeometry(QtCore.QRect(10, 20, 81, 71))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_loadMovie.setFont(font)
        self.pushButton_loadMovie.setAutoFillBackground(False)
        self.pushButton_loadMovie.setStyleSheet("background-color: lightgray")
        self.pushButton_loadMovie.setObjectName("pushButton_loadMovie")
        self.pushButton_clear = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_clear.setEnabled(True)
        self.pushButton_clear.setGeometry(QtCore.QRect(660, 20, 81, 71))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_clear.setFont(font)
        self.pushButton_clear.setAutoFillBackground(False)
        self.pushButton_clear.setStyleSheet("background-color: lightgray")
        self.pushButton_clear.setObjectName("pushButton_clear")
        self.graphicsView_movieView = GraphicsLayoutWidget(self.centralwidget)
        self.graphicsView_movieView.setGeometry(QtCore.QRect(15, 101, 721, 511))
        self.graphicsView_movieView.setObjectName("graphicsView_movieView")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1004, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.actionQuit = QtWidgets.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("res/remove.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionQuit.setIcon(icon6)
        self.actionQuit.setObjectName("actionQuit")
        self.action_load_movie = QtWidgets.QAction(MainWindow)
        self.action_load_movie.setObjectName("action_load_movie")
        self.action_load_hdf5 = QtWidgets.QAction(MainWindow)
        self.action_load_hdf5.setObjectName("action_load_hdf5")
        self.actionAvi = QtWidgets.QAction(MainWindow)
        self.actionAvi.setObjectName("actionAvi")
        self.actionTiff_stack = QtWidgets.QAction(MainWindow)
        self.actionTiff_stack.setObjectName("actionTiff_stack")
        self.actionPlots = QtWidgets.QAction(MainWindow)
        self.actionPlots.setObjectName("actionPlots")
        self.actionSettings = QtWidgets.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.action_save_avi = QtWidgets.QAction(MainWindow)
        self.action_save_avi.setObjectName("action_save_avi")
        self.action_save_hdf5 = QtWidgets.QAction(MainWindow)
        self.action_save_hdf5.setObjectName("action_save_hdf5")
        self.action_save_tiff = QtWidgets.QAction(MainWindow)
        self.action_save_tiff.setObjectName("action_save_tiff")
        self.action_load_tiff = QtWidgets.QAction(MainWindow)
        self.action_load_tiff.setObjectName("action_load_tiff")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionModel = QtWidgets.QAction(MainWindow)
        self.actionModel.setObjectName("actionModel")
        self.action_custom_algorithm = QtWidgets.QAction(MainWindow)
        self.action_custom_algorithm.setObjectName("action_custom_algorithm")
        self.actionVideo = QtWidgets.QAction(MainWindow)
        self.actionVideo.setObjectName("actionVideo")
        self.actionLoad = QtWidgets.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("res/load.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLoad.setIcon(icon7)
        self.actionLoad.setObjectName("actionLoad")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Eyetracker"))
        self.groupBox_pupil.setTitle(_translate("MainWindow", "Pupil"))
        self.label_pupilBinary.setText(_translate("MainWindow", "Binary Thresh (uint8)"))
        self.label_pupilMinSize.setText(_translate("MainWindow", "Min Size (uint)"))
        self.label_pupilROI.setText(_translate("MainWindow", "ROI"))
        self.label_pupilBlur.setText(_translate("MainWindow", "Blur (uint)"))
        self.label_pupilOpenClose.setText(_translate("MainWindow", "Open Close (uint)"))
        self.label_pupilEqualize.setText(_translate("MainWindow", "Equalize"))
        self.label_pupilROIValue.setText(_translate("MainWindow", "None"))
        self.groupBox_led.setTitle(_translate("MainWindow", "LED"))
        self.label_ledBlur.setText(_translate("MainWindow", "Blur (uint)"))
        self.label_ledOpenClose.setText(_translate("MainWindow", "Open Close (uint)"))
        self.label.setText(_translate("MainWindow", "Mask dilation (uint)"))
        self.label_ledBinary.setText(_translate("MainWindow", "Binary Thresh (uint8)"))
        self.label_led_min.setText(_translate("MainWindow", "Min Size (float)"))
        self.label_ledROI.setText(_translate("MainWindow", "ROI"))
        self.label_ledMaxSize.setText(_translate("MainWindow", "Max Size (float)"))
        self.label_ledROIValue.setText(_translate("MainWindow", "None"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Results"))
        self.groupBox_movieInfo.setTitle(_translate("MainWindow", "Movie Info"))
        self.label_moviePath.setText(_translate("MainWindow", "File path:"))
        self.label_movieFrameNumber.setText(_translate("MainWindow", "Total Frame Number :"))
        self.label_moviePathValue.setText(_translate("MainWindow", "None"))
        self.label_movieFrameNumberValue.setText(_translate("MainWindow", "None"))
        self.label_movieFrameShape.setText(_translate("MainWindow", "Frame shape (height, width) : "))
        self.label_movieFrameShapeValue.setText(_translate("MainWindow", "None"))
        self.lineEdit_currframeNum.setText(_translate("MainWindow", "0"))
        self.pushButton_loadMovie.setText(_translate("MainWindow", "LOAD"))
        self.pushButton_clear.setText(_translate("MainWindow", "CLEAR"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.action_load_movie.setText(_translate("MainWindow", "movie"))
        self.action_load_hdf5.setText(_translate("MainWindow", "hdf5"))
        self.actionAvi.setText(_translate("MainWindow", "avi"))
        self.actionTiff_stack.setText(_translate("MainWindow", "hdf5"))
        self.actionPlots.setText(_translate("MainWindow", "Plots"))
        self.actionSettings.setText(_translate("MainWindow", "Settings"))
        self.action_save_avi.setText(_translate("MainWindow", "avi"))
        self.action_save_hdf5.setText(_translate("MainWindow", "hdf5"))
        self.action_save_tiff.setText(_translate("MainWindow", "tiff stack"))
        self.action_load_tiff.setText(_translate("MainWindow", "tiff stack"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionModel.setText(_translate("MainWindow", "Model"))
        self.action_custom_algorithm.setText(_translate("MainWindow", "custom algorithm"))
        self.actionVideo.setText(_translate("MainWindow", "Video"))
        self.actionLoad.setText(_translate("MainWindow", "Load"))

from pyqtgraph import GraphicsLayoutWidget

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

