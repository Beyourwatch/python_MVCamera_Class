from __future__ import print_function
import sys
from mvIMPACT import acquire
from mvIMPACT.Common import exampleHelper
import ctypes
import numpy
import cv2
import threading
import ContinuousCapture as mvcamera


exitFlag = 0

class myThread (threading.Thread):
    def __init__(self, threadID, camera):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.camera = camera

    def run(self):
        print("开始线程：" + self.name)
        self.camera.openAcquisitionEngine()
        print("退出线程：" + self.name)

# 创建新线程


camera1 = mvcamera.MV_Camera(0)
print(type(camera1))
print(type(camera1.cameraDevice))
print(camera1.cameraserial)

camera1.opencamera()


camera1.setupcamera()

thread1 = myThread("Thread_1", camera1)

# 开启新线程
thread1.start()
thread1.join()
print("退出主线程")


input()