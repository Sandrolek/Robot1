#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RTCjoystick
import xmlrpc.client
import time

import receiver

IP_ROBOT = '192.168.1.175' # Дом
# IP_ROBOT = '192.168.8.161' # Школа
PORT_GS = 5000

recv = receiver.StreamReceiver(receiver.FORMAT_H264, (IP_ROBOT, PORT_GS))
recv.play_pipeline()
print('Waiting for GStream video pipline from IP:%s on PORT:%d' % (IP_ROBOT, PORT_GS))

PORT_XMLSERVER = 8000
strServer = 'http://'+str(IP_ROBOT)+':'+str(PORT_XMLSERVER)
#strServer = 'http://192.168.1.175:8000'
s = xmlrpc.client.ServerProxy(strServer)
print('Connect to XMLServer:' + strServer)

leftSpeed = 0
rightSpeed = 0
lastRightSp = 0
lastLeftSp = 0
SPEED = 100
speedChange = False

#инициализируем переменные значения кнопок и их названия (и то же самое для стиков) 
start = 0
hatX = 0.0
hatY = 0.0
turning = 'hat0x'
direct = 'hat0y'
startTrans = 'start'


J = RTCjoystick.Joystick()
J.connect("/dev/input/js0")
J.info()
J.start()

def btn_start():
    s.start('Button "Start" is pressed')
    #print('Button "Start" is pressed')

J.connectButton(startTrans, btn_start)

hatXOld = 0.0
hatYOld = 0.0
BASE_SPEED = 200
speedChange = False

try:
    while True:
        hatX = J.Axis.get(turning)
        hatY = J.Axis.get(direct)
        #print(hatX, hatY)

        if hatX != hatXOld:
            #print("HatX is pressed")
            if hatX != 0:
                leftSpeed = round(hatX * BASE_SPEED / 2)
                rightSpeed = round(hatX * BASE_SPEED / 2)
            else:
                leftSpeed = 0
                rightSpeed = 0
            speedChange = True
            hatXOld = hatX

        if hatY != hatYOld:
            #print("HatY is pressed")
            if hatY != 0:
                leftSpeed = round(-hatY * BASE_SPEED / 2)
                rightSpeed = round(hatY * BASE_SPEED / 2)
            else:
                leftSpeed = 0
                rightSpeed = 0
            speedChange = True
            hatYOld = hatY

        if speedChange:
            print('LeftSpeed = %d, RightSpeed = %d' % (leftSpeed, rightSpeed))
            #print("ChangeSpeed is True")
            s.Motors(leftSpeed, rightSpeed)
            #print("It was...")
            speedChange = False

        time.sleep(0.1)

except(KeyboardInterrupt, SystemExit):
    print('Ctrl+C pressed')
    recv.stop_pipeline()
    recv.null_pipeline()
    J.exit()

'''
        if hatX != 0: # Нажата либо Левая либо Правая
            #print('Not 0')
            leftSpeed = hatX*SPEED
            rightSpeed = hatX*SPEED
        elif hatY != 0:
            leftSpeed = -hatY*SPEED
            rightSpeed = hatY*SPEED
        elif hatX == 0 or hatY == 0:
            leftSpeed = 0
            rightSpeed = 0

        if leftSpeed == lastLeftSp and rightSpeed == lastRightSp:
            speedChange = False
        else:
            speedChange = True

        if speedChange == True:
            print('Left speed = %d, Right speed = %d' % (leftSpeed, rightSpeed))
            s.Motors(leftSpeed, rightSpeed)
            lastLeftSp = leftSpeed
            lastRightSp = rightSpeed
'''
