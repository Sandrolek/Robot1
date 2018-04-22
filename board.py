#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xmlrpc.server import SimpleXMLRPCServer
import subprocess
import time
import os
import psutil
import threading
from PIL import Image       # библиотеки для рисования на дисплее
from PIL import ImageDraw
from PIL import ImageFont

import gi
from gi.repository import GObject

# библиотеки РТК
import RPiPWM
import rpicam

# Видеопоток
FORMAT = rpicam.FORMAT_H264
WIDTH, HEIGHT = 640, 360
RESOLUTION = (WIDTH, HEIGHT)
FRAMERATE = 30

# Сеть
IP_ROBOT = '192.168.1.175'
IP_PULT  = '192.168.1.180'
PORT_GS                 = 5000
PORT_XMLSERVER_ROBOT    = 8000

# Порты моторов
chanRevMotorL = 12
chanRevMotorR = 13

# создаем объекты моторов
motorL = RPiPWM.ReverseMotor(chanRevMotorL)
motorR = RPiPWM.ReverseMotor(chanRevMotorR)

# Варианты как узнать свой IP, но для прозрачности конфигурирования прошиваем жестко
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
# cmd = 'hostname -I | cut -d\' \' -f1'
# IP_ROBOT = subprocess.check_output(cmd, shell = True) #получаем IP
# IP_ROBOT = IP_ROBOT.rstrip().decode("utf-8") #удаляем \n, переводим в текст

'''
# ВАРИАНТ как получить свой IP: Получаем свой IP адрес
IP = rpicam.getIP()
assert IP != '', 'Invalid IP address'
print('Robot IP address: %s' % IP)
'''

class SK_DisplayStatus(threading.Thread):
    def __init__(self, interval, adc):
        super(SK_DisplayStatus, self).__init__()
        self.daemon = True
        self.voltage = 0.0
        self.cpuTemp = 0
        self.cpuPercent = 0
        self.interval = interval
        self.stopped = threading.Event() # !!! КАК ЭТО РАБОТАЕТ ?
        self.adc = adc
        self.number_disp = True


    # функция, которая будет срабатывать при нажатии на кнопку
#    def ButtonEvent(self, a):  # обязательно должна иметь один аргумент
#        print("Somebody pressed button!")
#        self.number_disp = not self.number_disp


    def run(self):
        print('SK_DisplayStatus started')

#        gpio = RPiPWM.Gpio()
#        gpio.ButtonAddEvent(self.ButtonEvent)

        # создаем объект для работы с дисплеем (еще возможные варианты - 128_32 и 96_16 - размеры дисплеев в пикселях)
        disp = RPiPWM.SSD1306_128_64()
        disp.Begin()  # запускаем дисплей
        disp.Clear()  # очищаем буффер изображения
        disp.Display()  # выводим пустую картинку на дисплей

        width = disp.width  # получаем высоту и ширину дисплея
        height = disp.height

        image = Image.new('1', (width, height))  # создаем изображение из библиотеки PIL для вывода на экран
        draw = ImageDraw.Draw(image)  # создаем объект, которым будем рисовать
        top = -2  # сдвигаем текст вверх на 2 пикселя
        x = 0  # сдвигаем весь текст к левому краю
        font = ImageFont.load_default()  # загружаем стандартный шрифт

        while not self.stopped.wait(self.interval):
            self.cpuTemp    = rpicam.getCPUtemperature()
            self.cpuPercent = psutil.cpu_percent()
            self.voltage    = self.adc.GetVoltageFiltered()

            #print ('CPU temp: %.2f°C. CPU use: %.2f%% .Battery: %.2fV' % (
            #self.cpuTemp, self.cpuPercent, self.voltage))

            draw.rectangle((0, 0, width, height), outline=0, fill=0)  # очищаем дисплей

            if self.number_disp:
                draw.text((x, top), "Screen: 1 / 2", font=font, fill=255)
                draw.text((x, top + 8),  "Battery: "    + str(self.voltage)     + " V",  font=font, fill=255)  # высота строки - 8 пикселей
                draw.text((x, top + 16), "CPU Temp: "   + str(self.cpuTemp)     + " °C", font=font, fill=255)
                draw.text((x, top + 24), "CPU Percent: "+ str(self.cpuPercent)  + " %",  font=font, fill=255)
                draw.text((x, top + 32), "...",                                          font=font, fill=255)
                draw.text((x, top + 40), "...",                                          font=font, fill=255)
                draw.text((x, top + 48), "...",                                          font=font, fill=255)
            else:
                draw.text((x, top), "Screen: 2 / 2", font=font, fill=255)

            disp.Image(image)
            disp.Display()

#            gpio.LedToggle()  # переключаем светодиод

    def stop(self):
        self.stopped.set()

class SK_GStreamer():
    def __init__(self):
        super(SK_GStreamer, self).__init__()

#    def onFrameCallback(frame):
#        pass

    def start(self):
        print('SK_GStreamer started')

        # видеопоток с робота
        self.robotCamStreamer = rpicam.RPiCamStreamer(FORMAT, RESOLUTION, FRAMERATE, (IP_PULT, PORT_GS)) #, self.onFrameCallback)
#        self.robotCamStreamer.setRotation(180)
        self.robotCamStreamer.start()

    def stop(self):
        self.robotCamStreamer.stop()
        self.robotCamStreamer.close()

'''
class SK_CpuInfo(threading.Thread):
    def __init__(self, interval, adc):
        super(SK_CpuInfo, self).__init__()
        #threading.Thread.__init__(self)
        self.daemon = True
        self.interval = interval
        self.stopped = threading.Event()
        self.adc = adc

    def run(self):
        while not self.stopped.wait(self.interval):
            print ('CPU temp: %.2f°C. CPU use: %.2f%% .Battery: %.2fV' % (
            rpicam.getCPUtemperature(), psutil.cpu_percent(), self.adc.GetVoltageFiltered()))

    def stop(self):
        self.stopped.set()
'''

# Серверная функция: пустая функция, задел на будущее, обработка кнопки Start
def Start(word):
    print('Word = %s' % (word))
    return 0    
# Серверная функция: изменение скорости моторов
def Motors(leftSpeed, rightSpeed):
    print('LeftSpeed = %d, RightSpeed = %d' % (leftSpeed, rightSpeed))
    motorL.SetValue(leftSpeed)
    motorR.SetValue(rightSpeed)
    return 0
    # print('Right speed is %d, and left speed is %d' % (leftSpeed, rightSpeed))

assert rpicam.checkCamera(), 'Raspberry Pi camera not found'
print('Raspberry Pi camera found')

# создаем объект, который будет работать с АЦП
# указываем опорное напряжение, оно замеряется на первом пине Raspberry (обведено квадратом на шелкографии)
adc = RPiPWM.Battery(vRef=3.28)
adc.start()  # запускаем измерения

# нужно для корректной работы системы
# НЕ ПОНИМАЕМ КАК РАБОТАЕТ И ЗАЧЕМ НЕОБХОДИМА
GObject.threads_init()
mainloop = GObject.MainLoop()

skDisplayStatus = SK_DisplayStatus(1, adc)
skDisplayStatus.start()

skGStreamer = SK_GStreamer()
skGStreamer.start()

# set up the server
server = SimpleXMLRPCServer((IP_ROBOT, PORT_XMLSERVER_ROBOT))
server.logRequests = False
print('Listening on %s:%d' % (IP_ROBOT, PORT_XMLSERVER_ROBOT))

# register our functions
server.register_function(Start)
server.register_function(Motors)
Motors(0,0)

#запускаем сервер в отдельном потоке
serverControlThread = threading.Thread(target = server.serve_forever)
serverControlThread.daemon = True
serverControlThread.start()

#поток выдачи информации о процессоре 1 раз в сек
#cpuInfo = SK_CpuInfo(1, adc)
#cpuInfo.start()

#главный цикл программы
try:
    mainloop.run()
except (KeyboardInterrupt, SystemExit):
    print('Ctrl+C pressed')

Motors(0,0)

# останов трансляции камеры
skGStreamer.stop()
skDisplayStatus.stop()
server.server_close()
adc.stop()

# Run the server's main loop
#server.serve_forever()

#while True:
#    skDisplayStatus.SetVoltage(adc.GetVoltageFiltered())  # получаем напряжение аккумулятора
