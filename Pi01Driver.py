# -*- coding: utf-8 -*-
# @Time    : 2023/9/22 16:32
# @Author  : yifei.su
# @File    : tem.py.py

from IfDriver import *

def pi01_set_internal_vref(pBdg, value=True):
    """
    select pi01 vref
    :param pBdg: hid bridge object
    :param value: True - select internal vref
                  False - select external vref
    :return:
    """
    if value == True:
        i2c_write(pBdg, 0x20, 0x00, [0x0B, 0x02, 0x00])
    else:
        i2c_write(pBdg, 0x20, 0x00, [0x0B, 0x00, 0x00])


def pi01_set_adc_gain(pBdg, gain=1):
    """
    set adc gain
    :param pBdg: hid bridge object
    :param gain: 1 - gain is 1
                 2 - gain is 2
    :return:
    """
    if gain == 2:
        i2c_write(pBdg, 0x20, 0x00, [0x03, 0x01, 0x20])  # enable adc buffer and set gain as 2
    else:
        i2c_write(pBdg, 0x20, 0x00, [0x03, 0x01, 0x00])  # enable adc buffer and set gain as 1


def pi01_init_adc(pBdg):
    """
    set GP0~GP7 work as ADC input
    :param pBdg:
    :return:
    """
    i2c_write(pBdg, 0x20, 0x00, [0x06, 0x00, 0x00])  # disable pull-down
    i2c_write(pBdg, 0x20, 0x00, [0x04, 0x0f, 0x0f])  # set GP0~GP7 as adc input


def pi01_enable_adc(pBdg, channel=0x01):
    """
    enable selected channel adc data
    :param pBdg: hid bridge object
    :param channel: 0x01 - ch0
                    0x02 - ch1
                    0x04 - ch2
                    0x08 - ch3
                    0x10 - ch4
                    0x20 - ch5
                    0x40 - ch6
                    0x80 - ch7
    :return:
    """
    i2c_write(pBdg, 0x20, 0x00, [0x02, 0x02, channel])  # enable repeat and corresponding channel


def pi01_read_adc(pBdg):
    rdData = i2c_read(pBdg, 0x20, 0x00, 2, [0x40])
    hexData = [rdData[1], rdData[2]]
    return hexData