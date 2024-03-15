# -*- coding: utf-8 -*-
# @Time    : 2023/9/22 16:32
# @Author  : yifei.su
# @File    : tem.py.py

import time

from IfDriver import *


'''
@fn     pi08_input_register_write
@brief  写入数据到对应 channel 的 buffer register。
        该函数和 LOADb pin 配合使用，一般用在 asynchronous 模式，
        即写入数据后不马上更新到输出 pin 脚，直到 LOADb pin 出现下降沿，所有 channel 一起更新。
        注意：如果 LOADb pin 一直接地（synchronous 模式），则输入数据会马上更新到输出 pin 脚。
@param  pBdg - 和 PC 连接的 bridge board
        chNum - 选择 channel number. 
                由 4bit [3:0] 控制选择：
                0000: DAC0
                0001: DAC1
                0010: DAC2
                0011: DAC3
                ...
                0111: DAC7
                1111: All DAC's
        chData - output data. 16bit [15:0]
@return none
'''
def pi08_input_register_write(pBdg, chNum=0x0, chData=0x8000):
    regData = 0x00000000 | (chNum << 20) | (chData << 4)      # command 0x0
    byte1 = (regData >> 24) & 0xFF
    byte2 = (regData >> 16) & 0xFF
    byte3 = (regData >> 8) & 0xFF
    byte4 = regData & 0xFF
    data = [byte1, byte2, byte3, byte4]
    hid_spi_write(pBdg, data)

'''
@fn     pi08_channel_output_update
@brief  此函数通常应用在 asynchronous 模式下，用来更新 output pin 输出。
        执行此函数后，指定 channel output pin 输出，按当前其对应 buffer register 中的值进行更新。
@param  ctrComBd - 和 PC 用 COM 连接的 control board
        chNum - 选择 channel number. 
                由 4bit [3:0] 控制选择：
                0000: DAC0
                0001: DAC1
                0010: DAC2
                0011: DAC3
                ...
                0111: DAC7
                1111: All DAC's
@return none
'''
def pi08_channel_output_update(pBdg, chNum=0x0):
    regData = 0x01000000 | (chNum << 20)       # command 0x1
    byte1 = (regData >> 24) & 0xFF
    byte2 = (regData >> 16) & 0xFF
    byte3 = (regData >> 8) & 0xFF
    byte4 = regData & 0xFF
    data = [byte1, byte2, byte3, byte4]
    hid_spi_write(pBdg, data)


'''
@fn     pi08_set_channel_update_all
@brief  该函数应用在软件控制 asynchronous 场景。
        asynchronous 模式下，最后一个配置 channel 调用该函数，
        函数执行后，会触发所有 channel output pin 更新
@param  ctrComBd - 和 PC 用 COM 连接的 control board
        chNum - 选择 channel number. 
                由 4bit [3:0] 控制选择：
                0000: DAC0
                0001: DAC1
                0010: DAC2
                0011: DAC3
                ...
                0111: DAC7
                1111: All DAC's
        chData - output data. 16bit [15:0]
@return none
'''
def pi08_set_channel_update_all(pBdg, chNum=0x0, chData=0x8000):
    regData = 0x02000000 | (chNum << 20) | (chData << 4)      # command 0x2
    byte1 = (regData >> 24) & 0xFF
    byte2 = (regData >> 16) & 0xFF
    byte3 = (regData >> 8) & 0xFF
    byte4 = regData & 0xFF
    data = [byte1, byte2, byte3, byte4]
    hid_spi_write(pBdg, data)


'''
@fn     pi08_set_channel_output
@brief  该函数应用在 synchronous 模式，
        即给某个 channel 输入数据后，对应 output pin 马上更新。
@param  ctrComBd - 和 PC 用 COM 连接的 control board
        chNum - 选择 channel number. 
                由 4bit [3:0] 控制选择：
                0000: DAC0
                0001: DAC1
                0010: DAC2
                0011: DAC3
                ...
                0111: DAC7
                1111: All DAC's
        chData - output data. 16bit [15:0]
@return none
'''
def pi08_set_channel_output(pBdg, chNum=0x0, chData=0x8000):
    regData = 0x03000000 | (chNum << 20) | (chData << 4)      # command 0x3
    byte1 = (regData >> 24) & 0xFF
    byte2 = (regData >> 16) & 0xFF
    byte3 = (regData >> 8) & 0xFF
    byte4 = regData & 0xFF
    data = [byte1, byte2, byte3, byte4]
    hid_spi_write(pBdg, data)


'''
@fn     pi08_channel_power_down
@brief  设置各 channel 是否 power down 以及 power down 输出值
@param  ctrComBd - 和 PC 用 COM 连接的 control board
        pdMode - 指定 power down 模式。 2bit [1:0]
            b00: operating mode
            b01: Power Down with outputs connected to GND with 1kohm
            b10: Power Down with outputs connected to GND with 10kohm
            b11: Power Down with outputs high impedance
        pdChaNum - 用于指定执行 power down 的 channel. 8bit, [7:0] 
@return none
'''
def pi08_channel_power_down(pBdg, pdMode = 0x3, pdChaNum = 0x00):
    regData = 0x04000000 | (pdMode << 8) | pdChaNum                # command 0x4
    byte1 = (regData >> 24) & 0xFF
    byte2 = (regData >> 16) & 0xFF
    byte3 = (regData >> 8) & 0xFF
    byte4 = regData & 0xFF
    data = [byte1, byte2, byte3, byte4]
    hid_spi_write(pBdg, data)


'''
@fn     pi08_set_clear_code
@brief  设置 PRESETb 拉低（执行硬件 reset）时，VDAC output pin 脚输出的值
@param  ctrComBd - 和 PC 用 COM 连接的 control board
        crCode - clear code。 
            共有 4 种输出值，由 2bit [1:0] 来选择: 
            b00 - Clears to 0x0000
            b01 -  Clears to 0x8000
            b10 - Clears to 0xFFFF
            b11 - No operation
@return none
'''
def pi08_set_clear_code(pBdg, crMode = 0x0):
    regData = 0x05000000 | crMode            # command 0x5
    byte1 = (regData >> 24) & 0xFF
    byte2 = (regData >> 16) & 0xFF
    byte3 = (regData >> 8) & 0xFF
    byte4 = regData & 0xFF
    data = [byte1, byte2, byte3, byte4]
    hid_spi_write(pBdg, data)


'''
@fn     pi08_set_channel_load_mode
@brief  设置输入数据到 output pin 更新的同步方式，是否由 LOADb pin 硬件控制
@param  ctrComBd - 和 PC 用 COM 连接的 control board
        chLdMode - 各 channel 的 load mode。 
            8bit [7:0]: 每一个 bit 代表一个 channel
            对应 bit 等于 0： hardware LOADb control
                            LOADb pin = 0: synchronous 模式，即输入数据马上更新到输出 pin 脚
                            LOADb pin = 1: asynchronous 模式，输入数据不马上更新，直到 LOADb pin 出现下降沿才更新
            对应 bit 等于 1： disable hardware LOADb control
                            该 channel 不受 LOADb pin 控制，只要有输入数据就马上更新到输出 pin 脚
@return none
'''
def pi08_set_channel_load_mode(pBdg, chLdMode=0x00):
    regData = 0x06000000 | chLdMode          # command 0x6
    byte1 = (regData >> 24) & 0xFF
    byte2 = (regData >> 16) & 0xFF
    byte3 = (regData >> 8) & 0xFF
    byte4 = regData & 0xFF
    data = [byte1, byte2, byte3, byte4]
    hid_spi_write(pBdg, data)


'''
@fn     pi08_soft_reset
@brief  software reset
@param  ctrComBd - 和 PC 用 COM 连接的 control board        
@return none
'''
def pi08_soft_reset(pBdg):
    regData = 0x07000000  # command 0x7
    byte1 = (regData >> 24) & 0xFF
    byte2 = (regData >> 16) & 0xFF
    byte3 = (regData >> 8) & 0xFF
    byte4 = regData & 0xFF
    data = [byte1, byte2, byte3, byte4]
    hid_spi_write(pBdg, data)


'''
@fn     pi08_set_ref
@brief  设置使用内部还是外部 vref
@param  ctrComBd - 和 PC 用 COM 连接的 control board
        refMode - vref 提供方式
            由 1 个 bit 来设置：
            0：使用外部 reference (default)
            1: 使用内部 reference
@return none
'''
def pi08_set_ref(pBdg, refMode=0x0):
    regData = 0x08000000 | refMode           # command 0x8
    byte1 = (regData >> 24) & 0xFF
    byte2 = (regData >> 16) & 0xFF
    byte3 = (regData >> 8) & 0xFF
    byte4 = regData & 0xFF
    data = [byte1, byte2, byte3, byte4]
    hid_spi_write(pBdg, data)


'''
@fn     pi08_set_channel_range
@brief  设置各 channel 的 range
@param  ctrComBd - 和 PC 用 COM 连接的 control board
        chRange - 各 channel 的 range.
            8bit [7:0]: 每一个 bit 代表一个 channel
            对应 bit 等于 0： range 等于 vref
            对应 bit 等于 1： range 等于 2*vref
@return none
'''
def pi08_set_channel_range(pBdg, chRange=0x00):
    regData = 0x09000000 | chRange           # command 0x9
    byte1 = (regData >> 24) & 0xFF
    byte2 = (regData >> 16) & 0xFF
    byte3 = (regData >> 8) & 0xFF
    byte4 = regData & 0xFF
    data = [byte1, byte2, byte3, byte4]
    hid_spi_write(pBdg, data)


'''
@fn     pi08_unlock
@brief  unlock operation
@return none
'''
def pi08_unlock(pBdg):
    regData = 0x0A0CAFE0
    byte1 = (regData >> 24) & 0xFF
    byte2 = (regData >> 16) & 0xFF
    byte3 = (regData >> 8) & 0xFF
    byte4 = regData & 0xFF
    data = [byte1, byte2, byte3, byte4]
    hid_spi_write(pBdg, data)
    time.sleep(0.01)
    regData = 0x0A1C0C00
    byte1 = (regData >> 24) & 0xFF
    byte2 = (regData >> 16) & 0xFF
    byte3 = (regData >> 8) & 0xFF
    byte4 = regData & 0xFF
    data = [byte1, byte2, byte3, byte4]
    hid_spi_write(pBdg, data)


'''
@fn     pi08_set_debug_register
@brief  配置 trim register
@param  cmd - command. 4bit [3:0]
              0xA or 0xB
        regAddr - register address. 4bit [3:0]
        regData - register data. 16bit [15:0]
@return none
'''
def pi08_set_debug_register(pBdg, cmd=0xA, regAddr=0x0, regDat=0x0000):
    regData = 0x00000000 | (cmd << 24) | (regAddr << 20) | (regDat << 4)
    byte1 = (regData >> 24) & 0xFF
    byte2 = (regData >> 16) & 0xFF
    byte3 = (regData >> 8) & 0xFF
    byte4 = regData & 0xFF
    data = [byte1, byte2, byte3, byte4]
    hid_spi_write(pBdg, data)


'''
@fn     pi08_read_debug_register
@brief  pi08 read debug register
@param  msb - MSB region. 4bit [3:0]
              0x0, 0x1, 0x2, 0x3 or 0x4
        cmd - command region. 4bit [3:0]
              0xC or 0xD
        regAddr - register address. 4bit [3:0]
@return none
'''
def pi08_read_debug_register(pBdg, msb=0x0, cmd=0xC, regAddr=0x0):
    # regData = 0x00000000 | (msb << 28) | (cmd << 24) | (regAddr << 20)
    # byte1 = (regData >> 24) & 0xFF
    # byte2 = (regData >> 16) & 0xFF
    # byte3 = (regData >> 8) & 0xFF
    # byte4 = regData & 0xFF
    # data = [byte1, byte2, byte3, byte4]
    # hid_spi_write(pBdg, data)
    # time.sleep(0.5)
    rdData = hid_spi_read(pBdg, 4)
    return rdData


'''
@fn     pi08_set_trim_register
@brief  配置 trim register
@param  regAddr - register address. 5bit [4:0]
        regData - register data. 8bit [7:0]
@return none
'''
def pi08_set_trim_register(pBdg, regAddr=0x00, regData=0x00):
    regData = 0x0E000000 | (regAddr << 20) | (regData << 4)
    byte1 = (regData >> 24) & 0xFF
    byte2 = (regData >> 16) & 0xFF
    byte3 = (regData >> 8) & 0xFF
    byte4 = regData & 0xFF
    data = [byte1, byte2, byte3, byte4]
    hid_spi_write(pBdg, data)


'''
@fn     pi08_read_trim_register
@brief  pi08 read trim register
@param  regAddr - register address. 5bit [4:0]
@return none
'''
def pi08_read_trim_register(pBdg, regAddr=0x1F):
    # regData = 0x0C000000 | (regAddr << 20)
    # byte1 = (regData >> 24) & 0xFF
    # byte2 = (regData >> 16) & 0xFF
    # byte3 = (regData >> 8) & 0xFF
    # byte4 = regData & 0xFF
    # data = [byte1, byte2, byte3, byte4]
    # hid_spi_write(pBdg, data)
    # time.sleep(0.5)
    rdData = hid_spi_read(pBdg, 4)
    return rdData


'''
@fn     pi08_enable_spi_read
@brief  enable pi08 spi read function
@return none
'''
def pi08_enable_spi_read(pBdg):
    pi08_unlock(pBdg)
    time.sleep(0.5)
    regData = 0x0B011800
    byte1 = (regData >> 24) & 0xFF
    byte2 = (regData >> 16) & 0xFF
    byte3 = (regData >> 8) & 0xFF
    byte4 = regData & 0xFF
    data = [byte1, byte2, byte3, byte4]
    hid_spi_write(pBdg, data)