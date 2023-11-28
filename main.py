import binascii

from IfDriver import *
from Pi08Driver import *
from Pi01Driver import *

import hid
import time

import sys
from PyQt5.QtWidgets import *
from pi08 import Ui_MainWindow
from PyQt5.QtCore import *

import ctypes
import ctypes.wintypes as wintypes
from ctypes.wintypes import MSG


NULL = 0
INVALID_HANDLE_VALUE = -1
DBT_DEVTYP_DEVICEINTERFACE = 5
DEVICE_NOTIFY_WINDOW_HANDLE = 0x00000000
DBT_DEVICEREMOVECOMPLETE = 0x8004
DBT_DEVICEARRIVAL = 0x8000
WM_DEVICECHANGE = 0x0219

user32 = ctypes.windll.user32
RegisterDeviceNotification = user32.RegisterDeviceNotificationW
UnregisterDeviceNotification = user32.UnregisterDeviceNotification


class GUID(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("Data1", ctypes.c_ulong),
                ("Data2", ctypes.c_ushort),
                ("Data3", ctypes.c_ushort),
                ("Data4", ctypes.c_ubyte * 8)]


class DEV_BROADCAST_DEVICEINTERFACE(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("dbcc_size", wintypes.DWORD),
                ("dbcc_devicetype", wintypes.DWORD),
                ("dbcc_reserved", wintypes.DWORD),
                ("dbcc_classguid", GUID),
                ("dbcc_name", ctypes.c_wchar * 260)]


class DEV_BROADCAST_HDR(ctypes.Structure):
    _fields_ = [("dbch_size", wintypes.DWORD),
                ("dbch_devicetype", wintypes.DWORD),
                ("dbch_reserved", wintypes.DWORD)]

# GUID_DEVCLASS_PORTS = GUID(0x4D36E978, 0xE325, 0x11CE,
#                            (ctypes.c_ubyte * 8)(0xBF, 0xC1, 0x08, 0x00, 0x2B, 0xE1, 0x03, 0x18))
GUID_DEVINTERFACE_USB_DEVICE = GUID(0xA5DCBF10, 0x6530, 0x11D2,
                                    (ctypes.c_ubyte * 8)(0x90, 0x1F, 0x00, 0xC0, 0x4F, 0xB9, 0x51, 0xED))

target_pid = 0xfe07  # 用你的目标PID替换这里
target_vid = 0x1a86  # 用你的目标VID替换这里


class Pi08DemoWindow(QMainWindow, Ui_MainWindow):
    hidBdg = hid.device()       # add hid device object
    hidStatus = False           # False - hid open failed
                                # True - hid open successful

    def __init__(self, parent=None):
        super(Pi08DemoWindow, self).__init__(parent)
        self.setupUi(self)
        self.setupNotification()
        self.initUI()
        hide = [self.pushButton_openHid, self.pushButton_closeHid]
        for hide_component in hide:
            hide_component.setVisible(False)

    def select_pi08_channel(self):
        cs = []
        if self.radioButton_dac0.isChecked():
            cs = [0x0, 0x01]
        elif self.radioButton_dac1.isChecked():
            cs = [0x1, 0x02]
        elif self.radioButton_dac2.isChecked():
            cs = [0x2, 0x04]
        elif self.radioButton_dac3.isChecked():
            cs = [0x3, 0x08]
        elif self.radioButton_dac4.isChecked():
            cs = [0x4, 0x10]
        elif self.radioButton_dac5.isChecked():
            cs = [0x5, 0x20]
        elif self.radioButton_dac6.isChecked():
            cs = [0x6, 0x40]
        elif self.radioButton_dac7.isChecked():
            cs = [0x7, 0x80]
        elif self.radioButton_allDac.isChecked():
            cs = [0xf, 0xff]
        return cs


    def select_pi01_channel(self):
        cs = 0x00
        if self.radioButton_adcDac0.isChecked():
            cs = 0x01
        elif self.radioButton_adcDac1.isChecked():
            cs = 0x02
        elif self.radioButton_adcDac2.isChecked():
            cs = 0x04
        elif self.radioButton_adcDac3.isChecked():
            cs = 0x08
        elif self.radioButton_adcDac4.isChecked():
            cs = 0x10
        elif self.radioButton_adcDac5.isChecked():
            cs = 0x20
        elif self.radioButton_adcDac6.isChecked():
            cs = 0x40
        elif self.radioButton_adcDac7.isChecked():
            cs = 0x80
        else:
            cs = 0x00
        return cs

    def setupNotification(self):
        dbh = DEV_BROADCAST_DEVICEINTERFACE()
        dbh.dbcc_size = ctypes.sizeof(DEV_BROADCAST_DEVICEINTERFACE)
        dbh.dbcc_devicetype = DBT_DEVTYP_DEVICEINTERFACE
        dbh.dbcc_classguid = GUID_DEVINTERFACE_USB_DEVICE  # GUID_DEVCLASS_PORTS
        self.hNofity = RegisterDeviceNotification(int(self.winId()),
                                                  ctypes.byref(dbh),
                                                  DEVICE_NOTIFY_WINDOW_HANDLE)
        if self.hNofity == NULL:
            print(ctypes.FormatError(), int(self.winId()))
            # print("RegisterDeviceNotification failed")
        # else:
            # print("register successfully")

    def nativeEvent(self, eventType, msg):
        message = MSG.from_address(msg.__int__())
        if message.message == WM_DEVICECHANGE:
            self.onDeviceChanged(message.wParam, message.lParam)
        return False, 0

    def onDeviceChanged(self, wParam, lParam):
        if DBT_DEVICEARRIVAL == wParam:
            dev_info = ctypes.cast(lParam, ctypes.POINTER(DEV_BROADCAST_DEVICEINTERFACE)).contents
            device_path = ctypes.c_wchar_p(dev_info.dbcc_name).value
            cycCnt = 0
            if f"VID_{target_vid:04X}&PID_{target_pid:04X}" in device_path:
                while (self.open_hid() is not True) and (cycCnt < 3):
                    self.open_hid()
                    cycCnt += 1
                    # print(f'Target USB device inserted')

        elif DBT_DEVICEREMOVECOMPLETE == wParam:
            dev_info = ctypes.cast(lParam, ctypes.POINTER(DEV_BROADCAST_DEVICEINTERFACE)).contents
            device_path = ctypes.c_wchar_p(dev_info.dbcc_name).value
            if f"VID_{target_vid:04X}&PID_{target_pid:04X}" in device_path:
                self.close_hid()
                # print(f'Target USB device removed')


    def initUI(self):
        self.open_hid()

        self.radioButton_allDac.setChecked(True)
        self.lineEdit_value.setText("8000")
        self.radioButton_adcDac0.setChecked(True)

        self.pushButton_openHid.clicked.connect(self.open_hid)
        self.pushButton_closeHid.clicked.connect(self.close_hid)
        self.pushButton_writePart.clicked.connect(self.pi08_write_part)
        self.comboBox_dacVref.activated.connect(self.set_pi08_vref)
        self.comboBox_adcVref.activated.connect(self.set_pi01_vref)
        self.comboBox_adcGain.activated.connect(self.set_pi01_gain)
        self.pushButton_adcSample.clicked.connect(self.pi01_read_adc)
        self.checkBox_ldac.clicked.connect(self.pi08_check_ldac)
        self.checkBox_preset.clicked.connect(self.pi08_check_preset)

    def pi08_check_ldac(self):
        msgBoxWidget = QWidget()
        try:
            if self.hidStatus == True:
                if self.checkBox_ldac.isChecked():
                    gpio_write(self.hidBdg, 6, [1])
                else:
                    gpio_write(self.hidBdg, 6, [0])
            else:
                QMessageBox.information(msgBoxWidget, "Notification", "Please open HID first")
        except NameError as er:
            print(er)

    def pi08_check_preset(self):
        msgBoxWidget = QWidget()
        try:
            if self.hidStatus == True:
                if self.checkBox_preset.isChecked():
                    gpio_write(self.hidBdg, 7, [1])
                else:
                    gpio_write(self.hidBdg, 7, [0])
            else:
                QMessageBox.information(msgBoxWidget, "Notification", "Please open HID first")
        except NameError as er:
            print(er)


    def set_pi08_vref(self):
        msgBoxWidget = QWidget()
        try:
            if self.hidStatus == True:
                if self.comboBox_dacVref.currentText() == "Internal Vref":
                    pi08_set_ref(self.hidBdg, 1)
                elif self.comboBox_dacVref.currentText() == "External Vref":
                    pi08_set_ref(self.hidBdg, 0)
                else:
                    QMessageBox.information(msgBoxWidget, "Notification", "please select vref first")
            else:
                QMessageBox.information(msgBoxWidget, "Notification", "Please open HID first")
        except NameError as er:
            print(er)


    def pi08_write_part(self):
        msgBoxWidget = QWidget()
        try:
            if self.hidStatus == True:
                value_int = int(self.lineEdit_value.text(), 16)

                dac_ch = self.select_pi08_channel()

                if self.comboBox_regUpdate.currentText() == "Write to Input Register n":
                    pi08_input_register_write(self.hidBdg, dac_ch[0], value_int)
                elif self.comboBox_regUpdate.currentText() == "Update DAC Registet n":
                    pi08_channel_output_update(self.hidBdg, dac_ch[0])
                elif self.comboBox_regUpdate.currentText() == "Write Input n and Update All":
                    pi08_set_channel_update_all(self.hidBdg, dac_ch[0], value_int)
                elif self.comboBox_regUpdate.currentText() == "Write and Update Register n":
                    pi08_set_channel_output(self.hidBdg, dac_ch[0], value_int)
                elif self.comboBox_regUpdate.currentText() == "Power Down Operating Mode":
                    pi08_channel_power_down(self.hidBdg, 0x0, dac_ch[1])
                elif self.comboBox_regUpdate.currentText() == "Power Down to GND with 1K":
                    pi08_channel_power_down(self.hidBdg, 0x1, dac_ch[1])
                elif self.comboBox_regUpdate.currentText() == "Power Down to GND with 10K":
                    pi08_channel_power_down(self.hidBdg, 0x2, dac_ch[1])
                elif self.comboBox_regUpdate.currentText() == "Power Down to HI-Z":
                    pi08_channel_power_down(self.hidBdg, 0x3, dac_ch[1])
                elif self.comboBox_regUpdate.currentText() == "Clear to 0x0000":
                    pi08_set_clear_code(self.hidBdg, 0x0)
                elif self.comboBox_regUpdate.currentText() == "Clear to 0x8000":
                    pi08_set_clear_code(self.hidBdg, 0x1)
                elif self.comboBox_regUpdate.currentText() == "Clear to 0xFFFF":
                    pi08_set_clear_code(self.hidBdg, 0x2)
                elif self.comboBox_regUpdate.currentText() == "Clear No Operation":
                    pi08_set_clear_code(self.hidBdg, 0x3)
                elif self.comboBox_regUpdate.currentText() == "Set LDAC Channel":
                    pi08_set_clear_code(self.hidBdg, dac_ch[1] ^ dac_ch[1])
                elif self.comboBox_regUpdate.currentText() == "Chip Reset":
                    pi08_soft_reset(self.hidBdg)

            else:
                QMessageBox.information(msgBoxWidget, "Notification", "Please open HID first")
        except NameError as er:
            print(er)


    def set_pi01_vref(self):
        msgBoxWidget = QWidget()
        try:
            if self.hidStatus == True:
                if self.comboBox_adcVref.currentText() == "Internal Vref":
                    pi01_set_internal_vref(self.hidBdg, True)   # pi01 selects internal vref
                elif self.comboBox_adcVref.currentText() == "External Vref":
                    pi01_set_internal_vref(self.hidBdg, False)  # pi01 selects external vref
                else:
                    QMessageBox.information(msgBoxWidget, "Notification", "please select vref first")

                pi01_init_adc(self.hidBdg)          # set pi01 work as adc
                pi01_set_adc_gain(self.hidBdg, 1)   # set pi01 gain is vref
            else:
                QMessageBox.information(msgBoxWidget, "Notification", "Please open HID first")
        except NameError as er:
            print(er)


    def set_pi01_gain(self):
        msgBoxWidget = QWidget()
        try:
            if self.hidStatus == True:
                if self.comboBox_adcGain.currentText() == "Vref":
                    pi01_set_adc_gain(self.hidBdg, 1)
                elif self.comboBox_adcGain.currentText() == "Vref*2":
                    pi01_set_adc_gain(self.hidBdg, 2)
            else:
                QMessageBox.information(msgBoxWidget, "Notification", "Please open HID first")
        except NameError as er:
            print(er)


    def pi01_read_adc(self):
        msgBoxWidget = QWidget()
        try:
            if self.hidStatus == True:
                if self.select_pi01_channel() == 0x01:
                    pi01_enable_adc(self.hidBdg, 0x01)
                elif self.select_pi01_channel() == 0x02:
                    pi01_enable_adc(self.hidBdg, 0x02)
                elif self.select_pi01_channel() == 0x04:
                    pi01_enable_adc(self.hidBdg, 0x04)
                elif self.select_pi01_channel() == 0x08:
                    pi01_enable_adc(self.hidBdg, 0x08)
                elif self.select_pi01_channel() == 0x10:
                    pi01_enable_adc(self.hidBdg, 0x10)
                elif self.select_pi01_channel() == 0x20:
                    pi01_enable_adc(self.hidBdg, 0x20)
                elif self.select_pi01_channel() == 0x40:
                    pi01_enable_adc(self.hidBdg, 0x40)
                elif self.select_pi01_channel() == 0x80:
                    pi01_enable_adc(self.hidBdg, 0x80)
                else:
                    QMessageBox.information(msgBoxWidget, "Notification", "Please select channel")
                    return

                time.sleep(0.05)
                rdData = pi01_read_adc(self.hidBdg)
                rdValue = ((rdData[0]<<8) | rdData[1]) & 0x0FFF
                print(hex(rdValue))
                adcData = rdValue/4096 * 2.5
                self.lineEdit_adcData.setText("%f"%adcData + "V")
                # self.lineEdit_adcData.setText("%f" % 1.1925 + "V")
            else:
                QMessageBox.information(msgBoxWidget, "Notification", "Please open HID first")
        except NameError as er:
            print(er)



    def open_hid(self):
        """
        open hid device
        :return: True - open hid device successfully
                 False - open hid device failed
        """
        try:
            if self.hidStatus == False:
                self.hidBdg.open(0x1A86, 0xFE07)  # VendorID/ProductID
                self.statusBar().showMessage("open hid successfully")
                self.hidBdg.set_nonblocking(1)  # hid device enable non-blocking modepp
                self.hidStatus = True
                return self.hidStatus
            else:
                return self.hidStatus
        except:
            self.statusBar().showMessage("open hid failed")
            self.hidStatus = False
            return self.hidStatus


    def close_hid(self):
        """
        close hid device
        :return: True - close hid failed
                 False - close hid successfully  (note: return False means close successfully)
        """
        try:
            if self.hidStatus == True:
                self.hidBdg.close()
                self.statusBar().showMessage("close hid successfully")
                self.hidStatus = False
                return self.hidStatus
            else:
                return self.hidStatus
        except:
            self.statusBar().showMessage("close hid failed")
            self.hidStatus = True


if __name__ == '__main__':
    app = QApplication(sys.argv)

    win=Pi08DemoWindow()
    win.show()

    sys.exit(app.exec_())

    # hidDev = hid.device()
    # hidDev.open(0x1A86, 0xFE07) # open hid
    # hidDev.set_nonblocking(1)   # hid device enable non-blocking modepp
    #
    # hidDev.write([0x0a, 0x09, 0x01, 0x11, 0x00, 0x00, 0x04, 0x08, 0x00, 0x00, 0x01])

    # # """ spi write """
    # pi08_soft_reset(hidDev)     # reset pi08
    # pi08_set_ref(hidDev, 0x1)   # select internal vref
    # pi08_set_channel_output(hidDev, 0xf, 0x9C40)    # set all DAC channel output 0x9C40 (1.456V)
    #
    # """ i2c write """
    # pi01_set_internal_vref(hidDev, True)
    # pi01_set_adc_gain(hidDev, 1)
    # pi01_enable_adc(hidDev, 0x01)
    # print(pi01_read_adc(hidDev))

    # i2c_write(hidDev, 0x20, 0x00, [0x02, 0x01, 0x5A])
    # print(i2c_read(hidDev, 0x20, 0x00, 2, [0x72]))
