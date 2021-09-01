from __future__ import print_function
import sys
from mvIMPACT import acquire
from mvIMPACT.Common import exampleHelper
import ctypes
import numpy
import cv2



class MV_Camera():
    devMgr = ""
    cameraIndex = 0
    cameraserial = ""

    def __init__(self, index):
        self.cameraIndex = index
        self.devMgr = acquire.DeviceManager()
        self.cameraDevice = self.devMgr.getDevice(self.cameraIndex)
        self.cameraserial = self.cameraDevice.serial.readS()

    def opencamera(self):
        mvdevice = self.devMgr.getDeviceBySerial(self.cameraserial)
        mvdevice.interfaceLayout.writeS("GenICam")
        print("open camera index" + str(
            self.cameraIndex) + " " + mvdevice.product.readS() + " " + mvdevice.serial.readS())
        mvdevice.open()


    def setupcamera(self):
        print("setup camera")
        mvdevice = self.devMgr.getDeviceBySerial(self.cameraserial)
        mvIFControl = acquire.ImageFormatControl(mvdevice)
        mvID = acquire.ImageDestination(mvdevice)
        mvDVControl = acquire.DeviceControl(mvdevice)
        mvACControl = acquire.AcquisitionControl(mvdevice)

        fps = 10
        mvACControl.acquisitionFrameRate.write(fps)
        print("set camera fps = " + str(fps))

        if mvDVControl.mvDeviceSensorColorMode.readS() == "Grey":
            mvIFControl.pixelFormat.writeS("Mono8")
            mvID.pixelFormat.writeS("Mono8")
            print("Gray camera, set Pixel format to Mono8")
        else:
            pixelcolorfilter = mvIFControl.pixelColorFilter.readS()
            pixelcolorformat = pixelcolorfilter + "8"
            mvIFControl.pixelFormat.writeS(pixelcolorformat)
            mvID.pixelFormat.writeS(pixelcolorformat)
            print("Color camera, set Pixel format to " + pixelcolorformat)

    def openAcquisitionEngine(self):
        mvdevice = self.devMgr.getDeviceBySerial(self.cameraserial)
        fi = acquire.FunctionInterface(mvdevice)

        while fi.imageRequestSingle() == acquire.DMR_NO_ERROR:
            print("Buffer queued")
        pPreviousRequest = None

        exampleHelper.manuallyStartAcquisitionIfNeeded(mvdevice, fi)

        cv2.namedWindow(mvdevice.serial.readS(), cv2.WINDOW_NORMAL)
        cv2.resizeWindow(mvdevice.serial.readS(), 500, 500)
        for i in range(100):
            requestNr = fi.imageRequestWaitFor(-1)
            if fi.isRequestNrValid(requestNr):
                pRequest = fi.getRequest(requestNr)
                if pRequest.isOK:
                    print("Info from " + mvdevice.serial.readS() +
                          ": " + pRequest.imageWidth.readS() + "x" + pRequest.imageHeight.readS() +
                          ", " + pRequest.imagePixelFormat.readS() + " count " + str(i))

                cbuf = (ctypes.c_char * pRequest.imageSize.read()).from_address(int(pRequest.imageData.read()))
                channelType = numpy.uint16 if pRequest.imageChannelBitDepth.read() > 8 else numpy.uint8
                arr = numpy.frombuffer(cbuf, dtype=channelType)

                arr.shape = (pRequest.imageHeight.read(), pRequest.imageWidth.read(), pRequest.imageChannelCount.read())
                cv2.imshow(mvdevice.serial.readS(), arr)
                cv2.waitKey(10)

                if pPreviousRequest != None:
                    pPreviousRequest.unlock()
                pPreviousRequest = pRequest
                fi.imageRequestSingle()
            else:
                print("imageRequestWaitFor failed (" + str(
                requestNr) + ", " + acquire.ImpactAcquireException.getErrorCodeAsString(requestNr) + ")")

        cv2.destroyWindow("Window")
        exampleHelper.manuallyStopAcquisitionIfNeeded(mvdevice, fi)
