import os
import core.winframe as winframe
from tkinter import *
from core.pycfg import gamepath
import core.CacheContorl as cache
import time

textBox = winframe.textbox
imageData = {}
imageTextData = {}

# 获取图片数据
def getImageData(imageName,imagePath=''):
    if imagePath == '':
        imagePath = os.path.join(gamepath, 'image', imageName + '.png')
    else:
        imagePath = os.path.join(gamepath,'image',imagePath,imageName + '.png')
    image = PhotoImage(file=imagePath)
    cache.imageid = cache.imageid + 1
    return image

# 打印图片
def printImage(imageName,imagePath=''):
    time.sleep(0.01)
    imageData[str(cache.imageid)] = getImageData(imageName,imagePath)
    textBox.image_create(END,image = imageData[str(cache.imageid)])