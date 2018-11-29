# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'video.ui'
#
# Created: Mon Oct 06 14:40:39 2014
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(719, 503)
        Form.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("res/eye.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.graphicsView_img = GraphicsLayoutWidget(Form)
        self.graphicsView_img.setObjectName(_fromUtf8("graphicsView_img"))
        self.gridLayout.addWidget(self.graphicsView_img, 1, 0, 1, 2)
        self.label_frame_shape = QtGui.QLabel(Form)
        self.label_frame_shape.setObjectName(_fromUtf8("label_frame_shape"))
        self.gridLayout.addWidget(self.label_frame_shape, 0, 0, 1, 1)
        self.label_pixel_value = QtGui.QLabel(Form)
        self.label_pixel_value.setObjectName(_fromUtf8("label_pixel_value"))
        self.gridLayout.addWidget(self.label_pixel_value, 0, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "video", None))
        self.label_frame_shape.setText(_translate("Form", "image info", None))
        self.label_pixel_value.setText(_translate("Form", "pixel_value", None))

from pyqtgraph import GraphicsLayoutWidget
