# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/ui_files/monitor_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(902, 422)
        Dialog.setModal(False)
        self.gridLayout_4 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.lineEdit = QtWidgets.QLineEdit(self.tab)
        self.lineEdit.setEnabled(True)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout_3.addWidget(self.lineEdit, 1, 1, 1, 1)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.tab)
        self.lineEdit_3.setEnabled(True)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout_3.addWidget(self.lineEdit_3, 3, 1, 1, 1)
        self.line = QtWidgets.QFrame(self.tab)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_3.addWidget(self.line, 4, 0, 1, 2)
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.temperatureLabel = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.temperatureLabel.setFont(font)
        self.temperatureLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.temperatureLabel.setObjectName("temperatureLabel")
        self.gridLayout_5.addWidget(self.temperatureLabel, 1, 0, 1, 1)
        self.rxPowerLabel = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.rxPowerLabel.setFont(font)
        self.rxPowerLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.rxPowerLabel.setObjectName("rxPowerLabel")
        self.gridLayout_5.addWidget(self.rxPowerLabel, 5, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_7.setFont(font)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout_5.addWidget(self.label_7, 1, 2, 1, 1)
        self.laserTempLineEdit = QtWidgets.QLineEdit(self.tab)
        self.laserTempLineEdit.setObjectName("laserTempLineEdit")
        self.gridLayout_5.addWidget(self.laserTempLineEdit, 1, 3, 1, 1)
        self.tecCurrentLineEdit = QtWidgets.QLineEdit(self.tab)
        self.tecCurrentLineEdit.setObjectName("tecCurrentLineEdit")
        self.gridLayout_5.addWidget(self.tecCurrentLineEdit, 2, 3, 1, 1)
        self.vccLineEdit = QtWidgets.QLineEdit(self.tab)
        self.vccLineEdit.setObjectName("vccLineEdit")
        self.gridLayout_5.addWidget(self.vccLineEdit, 2, 1, 1, 1)
        self.rxPowerLineEdit = QtWidgets.QLineEdit(self.tab)
        self.rxPowerLineEdit.setObjectName("rxPowerLineEdit")
        self.gridLayout_5.addWidget(self.rxPowerLineEdit, 5, 1, 1, 1)
        self.txPowerLabel = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.txPowerLabel.setFont(font)
        self.txPowerLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txPowerLabel.setObjectName("txPowerLabel")
        self.gridLayout_5.addWidget(self.txPowerLabel, 4, 0, 1, 1)
        self.txBiasCurrentLabel = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.txBiasCurrentLabel.setFont(font)
        self.txBiasCurrentLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txBiasCurrentLabel.setObjectName("txBiasCurrentLabel")
        self.gridLayout_5.addWidget(self.txBiasCurrentLabel, 3, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout_5.addWidget(self.label_4, 0, 0, 1, 2)
        self.txPowerLineEdit = QtWidgets.QLineEdit(self.tab)
        self.txPowerLineEdit.setObjectName("txPowerLineEdit")
        self.gridLayout_5.addWidget(self.txPowerLineEdit, 4, 1, 1, 1)
        self.txBiasCurrentLineEdit = QtWidgets.QLineEdit(self.tab)
        self.txBiasCurrentLineEdit.setObjectName("txBiasCurrentLineEdit")
        self.gridLayout_5.addWidget(self.txBiasCurrentLineEdit, 3, 1, 1, 1)
        self.vccLabel = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.vccLabel.setFont(font)
        self.vccLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.vccLabel.setObjectName("vccLabel")
        self.gridLayout_5.addWidget(self.vccLabel, 2, 0, 1, 1)
        self.temperatureLineEdit = QtWidgets.QLineEdit(self.tab)
        self.temperatureLineEdit.setEnabled(True)
        self.temperatureLineEdit.setObjectName("temperatureLineEdit")
        self.gridLayout_5.addWidget(self.temperatureLineEdit, 1, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout_5.addWidget(self.label_6, 0, 2, 1, 2)
        self.label_8 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_8.setFont(font)
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout_5.addWidget(self.label_8, 2, 2, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_5, 5, 0, 1, 2)
        self.label = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 1, 0, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.tab)
        self.lineEdit_2.setEnabled(True)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout_3.addWidget(self.lineEdit_2, 2, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 2, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 2)
        self.label_3 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 3, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.txBiasHighWarnLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.txBiasHighWarnLineEdit.setObjectName("txBiasHighWarnLineEdit")
        self.gridLayout_7.addWidget(self.txBiasHighWarnLineEdit, 7, 2, 1, 1)
        self.txBiasLowWarnLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.txBiasLowWarnLineEdit.setObjectName("txBiasLowWarnLineEdit")
        self.gridLayout_7.addWidget(self.txBiasLowWarnLineEdit, 8, 2, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.tab_2)
        self.label_18.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_18.setObjectName("label_18")
        self.gridLayout_7.addWidget(self.label_18, 10, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.tab_2)
        self.label_12.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_12.setObjectName("label_12")
        self.gridLayout_7.addWidget(self.label_12, 4, 0, 1, 1)
        self.vccHighAlarmLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.vccHighAlarmLineEdit.setObjectName("vccHighAlarmLineEdit")
        self.gridLayout_7.addWidget(self.vccHighAlarmLineEdit, 5, 1, 1, 1)
        self.label_28 = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_28.setFont(font)
        self.label_28.setObjectName("label_28")
        self.gridLayout_7.addWidget(self.label_28, 0, 6, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.tab_2)
        self.label_15.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_15.setObjectName("label_15")
        self.gridLayout_7.addWidget(self.label_15, 7, 0, 1, 1)
        self.vccHighWarnLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.vccHighWarnLineEdit.setObjectName("vccHighWarnLineEdit")
        self.gridLayout_7.addWidget(self.vccHighWarnLineEdit, 5, 2, 1, 1)
        self.laserTempHighWarnLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.laserTempHighWarnLineEdit.setObjectName("laserTempHighWarnLineEdit")
        self.gridLayout_7.addWidget(self.laserTempHighWarnLineEdit, 3, 6, 1, 1)
        self.tempHighWarnLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.tempHighWarnLineEdit.setObjectName("tempHighWarnLineEdit")
        self.gridLayout_7.addWidget(self.tempHighWarnLineEdit, 3, 2, 1, 1)
        self.txPowerLowWarnLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.txPowerLowWarnLineEdit.setObjectName("txPowerLowWarnLineEdit")
        self.gridLayout_7.addWidget(self.txPowerLowWarnLineEdit, 10, 2, 1, 1)
        self.label_23 = QtWidgets.QLabel(self.tab_2)
        self.label_23.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_23.setObjectName("label_23")
        self.gridLayout_7.addWidget(self.label_23, 3, 4, 1, 1)
        self.laserTempHighAlarmLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.laserTempHighAlarmLineEdit.setObjectName("laserTempHighAlarmLineEdit")
        self.gridLayout_7.addWidget(self.laserTempHighAlarmLineEdit, 3, 5, 1, 1)
        self.tempLowAlarmLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.tempLowAlarmLineEdit.setObjectName("tempLowAlarmLineEdit")
        self.gridLayout_7.addWidget(self.tempLowAlarmLineEdit, 4, 1, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_21.setFont(font)
        self.label_21.setAlignment(QtCore.Qt.AlignCenter)
        self.label_21.setObjectName("label_21")
        self.gridLayout_7.addWidget(self.label_21, 0, 0, 1, 1)
        self.txPowerHighAlarmLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.txPowerHighAlarmLineEdit.setObjectName("txPowerHighAlarmLineEdit")
        self.gridLayout_7.addWidget(self.txPowerHighAlarmLineEdit, 9, 1, 1, 1)
        self.tempHighAlarmLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.tempHighAlarmLineEdit.setObjectName("tempHighAlarmLineEdit")
        self.gridLayout_7.addWidget(self.tempHighAlarmLineEdit, 3, 1, 1, 1)
        self.tempLowWarnLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.tempLowWarnLineEdit.setObjectName("tempLowWarnLineEdit")
        self.gridLayout_7.addWidget(self.tempLowWarnLineEdit, 4, 2, 1, 1)
        self.rxPowerLowWarnLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.rxPowerLowWarnLineEdit.setObjectName("rxPowerLowWarnLineEdit")
        self.gridLayout_7.addWidget(self.rxPowerLowWarnLineEdit, 12, 2, 1, 1)
        self.label_25 = QtWidgets.QLabel(self.tab_2)
        self.label_25.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_25.setObjectName("label_25")
        self.gridLayout_7.addWidget(self.label_25, 5, 4, 1, 1)
        self.laserTempLowAlarmLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.laserTempLowAlarmLineEdit.setObjectName("laserTempLowAlarmLineEdit")
        self.gridLayout_7.addWidget(self.laserTempLowAlarmLineEdit, 4, 5, 1, 1)
        self.rxPowerLowAlarmLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.rxPowerLowAlarmLineEdit.setObjectName("rxPowerLowAlarmLineEdit")
        self.gridLayout_7.addWidget(self.rxPowerLowAlarmLineEdit, 12, 1, 1, 1)
        self.vccLowAlarmLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.vccLowAlarmLineEdit.setObjectName("vccLowAlarmLineEdit")
        self.gridLayout_7.addWidget(self.vccLowAlarmLineEdit, 6, 1, 1, 1)
        self.txPowerLowAlarmLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.txPowerLowAlarmLineEdit.setObjectName("txPowerLowAlarmLineEdit")
        self.gridLayout_7.addWidget(self.txPowerLowAlarmLineEdit, 10, 1, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.tab_2)
        self.label_20.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_20.setObjectName("label_20")
        self.gridLayout_7.addWidget(self.label_20, 12, 0, 1, 1)
        self.tecCurrentLowWarnLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.tecCurrentLowWarnLineEdit.setObjectName("tecCurrentLowWarnLineEdit")
        self.gridLayout_7.addWidget(self.tecCurrentLowWarnLineEdit, 6, 6, 1, 1)
        self.tecCurrentLowAlarmLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.tecCurrentLowAlarmLineEdit.setObjectName("tecCurrentLowAlarmLineEdit")
        self.gridLayout_7.addWidget(self.tecCurrentLowAlarmLineEdit, 6, 5, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.gridLayout_7.addWidget(self.label_9, 0, 1, 1, 1)
        self.laserTempLowWarnLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.laserTempLowWarnLineEdit.setObjectName("laserTempLowWarnLineEdit")
        self.gridLayout_7.addWidget(self.laserTempLowWarnLineEdit, 4, 6, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem, 3, 3, 1, 1)
        self.label_27 = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_27.setFont(font)
        self.label_27.setObjectName("label_27")
        self.gridLayout_7.addWidget(self.label_27, 0, 5, 1, 1)
        self.label_24 = QtWidgets.QLabel(self.tab_2)
        self.label_24.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_24.setObjectName("label_24")
        self.gridLayout_7.addWidget(self.label_24, 4, 4, 1, 1)
        self.vccLowWarnLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.vccLowWarnLineEdit.setObjectName("vccLowWarnLineEdit")
        self.gridLayout_7.addWidget(self.vccLowWarnLineEdit, 6, 2, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.gridLayout_7.addWidget(self.label_10, 0, 2, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.tab_2)
        self.label_11.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_11.setObjectName("label_11")
        self.gridLayout_7.addWidget(self.label_11, 3, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.tab_2)
        self.label_14.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_14.setObjectName("label_14")
        self.gridLayout_7.addWidget(self.label_14, 6, 0, 1, 1)
        self.txPowerHighWarnLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.txPowerHighWarnLineEdit.setObjectName("txPowerHighWarnLineEdit")
        self.gridLayout_7.addWidget(self.txPowerHighWarnLineEdit, 9, 2, 1, 1)
        self.label_22 = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_22.setFont(font)
        self.label_22.setAlignment(QtCore.Qt.AlignCenter)
        self.label_22.setObjectName("label_22")
        self.gridLayout_7.addWidget(self.label_22, 0, 4, 1, 1)
        self.txBiasLowAlarmLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.txBiasLowAlarmLineEdit.setObjectName("txBiasLowAlarmLineEdit")
        self.gridLayout_7.addWidget(self.txBiasLowAlarmLineEdit, 8, 1, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.tab_2)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_7.addWidget(self.line_2, 13, 0, 1, 3)
        self.label_16 = QtWidgets.QLabel(self.tab_2)
        self.label_16.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_16.setObjectName("label_16")
        self.gridLayout_7.addWidget(self.label_16, 8, 0, 1, 1)
        self.rxPowerHighWarnLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.rxPowerHighWarnLineEdit.setObjectName("rxPowerHighWarnLineEdit")
        self.gridLayout_7.addWidget(self.rxPowerHighWarnLineEdit, 11, 2, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.tab_2)
        self.label_13.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_13.setObjectName("label_13")
        self.gridLayout_7.addWidget(self.label_13, 5, 0, 1, 1)
        self.tecCurrentHighWarnLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.tecCurrentHighWarnLineEdit.setObjectName("tecCurrentHighWarnLineEdit")
        self.gridLayout_7.addWidget(self.tecCurrentHighWarnLineEdit, 5, 6, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.tab_2)
        self.label_17.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_17.setObjectName("label_17")
        self.gridLayout_7.addWidget(self.label_17, 9, 0, 1, 1)
        self.label_19 = QtWidgets.QLabel(self.tab_2)
        self.label_19.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_19.setObjectName("label_19")
        self.gridLayout_7.addWidget(self.label_19, 11, 0, 1, 1)
        self.tecCurrentHighAlarmLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.tecCurrentHighAlarmLineEdit.setObjectName("tecCurrentHighAlarmLineEdit")
        self.gridLayout_7.addWidget(self.tecCurrentHighAlarmLineEdit, 5, 5, 1, 1)
        self.txBiasHighAlarmLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.txBiasHighAlarmLineEdit.setObjectName("txBiasHighAlarmLineEdit")
        self.gridLayout_7.addWidget(self.txBiasHighAlarmLineEdit, 7, 1, 1, 1)
        self.rxPowerHighAlarmLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.rxPowerHighAlarmLineEdit.setObjectName("rxPowerHighAlarmLineEdit")
        self.gridLayout_7.addWidget(self.rxPowerHighAlarmLineEdit, 11, 1, 1, 1)
        self.label_26 = QtWidgets.QLabel(self.tab_2)
        self.label_26.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_26.setObjectName("label_26")
        self.gridLayout_7.addWidget(self.label_26, 6, 4, 1, 1)
        self.line_3 = QtWidgets.QFrame(self.tab_2)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout_7.addWidget(self.line_3, 1, 0, 1, 7)
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout_4.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.temperatureLabel.setText(_translate("Dialog", "Temperature (C)"))
        self.rxPowerLabel.setText(_translate("Dialog", "RX Power (uW)"))
        self.label_7.setText(_translate("Dialog", "Laser Temperature/Wavelength"))
        self.txPowerLabel.setText(_translate("Dialog", "TX Power (uW)"))
        self.txBiasCurrentLabel.setText(_translate("Dialog", "TX Bias Current (mA)"))
        self.label_4.setText(_translate("Dialog", "Real Time Diagnostic Values"))
        self.vccLabel.setText(_translate("Dialog", "Vcc (V)"))
        self.label_6.setText(_translate("Dialog", "Optional Diagnostic Values"))
        self.label_8.setText(_translate("Dialog", "TEC current (>0 = cooling)"))
        self.label.setText(_translate("Dialog", "Module Vendor Name"))
        self.label_2.setText(_translate("Dialog", "Module Part Number"))
        self.label_5.setText(_translate("Dialog", "SFP+ Vendor Information"))
        self.label_3.setText(_translate("Dialog", "Diagnostic Monitoring Type"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Dialog", "Real Time Diagnostics"))
        self.label_18.setText(_translate("Dialog", "TX Power Low (uW)"))
        self.label_12.setText(_translate("Dialog", "Temperature Low (C)"))
        self.label_28.setText(_translate("Dialog", "Warning Threshold"))
        self.label_15.setText(_translate("Dialog", "TX Bias Current High (mA)"))
        self.label_23.setText(_translate("Dialog", "Laser Temp High (C)"))
        self.label_21.setText(_translate("Dialog", "Parameter"))
        self.label_25.setText(_translate("Dialog", "TEC Current High (mA)"))
        self.label_20.setText(_translate("Dialog", "RX Power Low (uW)"))
        self.label_9.setText(_translate("Dialog", "Alarm Threshold"))
        self.label_27.setText(_translate("Dialog", "Alarm Threshold"))
        self.label_24.setText(_translate("Dialog", "Laser Temp Low (C)"))
        self.label_10.setText(_translate("Dialog", "Warning Threshold"))
        self.label_11.setText(_translate("Dialog", "Temperature High (C)"))
        self.label_14.setText(_translate("Dialog", "Vcc Low (V)"))
        self.label_22.setText(_translate("Dialog", "Optional Parameter"))
        self.label_16.setText(_translate("Dialog", "TX Bias Current Low (mA)"))
        self.label_13.setText(_translate("Dialog", "Vcc High (V)"))
        self.label_17.setText(_translate("Dialog", "TX Power High (uW)"))
        self.label_19.setText(_translate("Dialog", "RX Power High (uW)"))
        self.label_26.setText(_translate("Dialog", "TEC Current Low (mA)"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Dialog", "Alarm/Warning Thresholds"))
