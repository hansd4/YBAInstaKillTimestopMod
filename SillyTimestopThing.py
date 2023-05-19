import os
import subprocess
import time
import pyautogui
import pygetwindow as gw
import numpy
import cv2
import dxcam
import ctypes

# CONSTS
r = 2 # the range of the colors (color 1 must be in the range of
       # color 2 plus or minus this num)
threshold = 255
grid_size = 4
rThreshold = 15
avgTarget = (65, 65, 65)
dThreshold = 4
avgIncreaseThreshold = 6
numIncreasesThreshold = 3
avgColorThreshold = 130
camera = dxcam.create()

debounce = False
lastRange = -1
lastAvg = 0
increaseCount = 0

def timestop():
    subprocess.call("taskkill /f /im RobloxPlayerBeta.exe", shell=True)
    os.startfile(r'C:\Users\hansa\Downloads\timestop.mov')
    time.sleep(3)
    subprocess.call("taskkill /f /im vlc.exe", shell=True)
    time.sleep(5)

def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call, shell=True).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())

def isTimestopped():
    startTime = time.time()
    global debounce, increaseCount, lastAvg
    print()
    if debounce:
        debounce = False
        return False
    # img = pyautogui.screenshot(region=(0, 23, 1920, 1017))
    img = camera.grab(region=(0, 0, 1920, 1080))
    if (not img is None and img.ndim > 0):
        avgColor = numpy.average(numpy.average(numpy.average(img, axis=0), axis=0), axis=0)
        # result = inRangeRGB(avgColor, avgTarget)
##        result = lowDeviation(avgColor)
        increase = avgColor - lastAvg
        lastAvg = avgColor
        if increase >= avgIncreaseThreshold:
            increaseCount += 1
        else:
            increaseCount = 0
        result = increaseCount >= numIncreasesThreshold and avgColor >= avgColorThreshold
        if (result):
            debounce = True
            increaseCount = 0
        print("Avg color: {0:.2f}. Took {1:.0f} ms".format(avgColor, 1000 * (time.time() - startTime)))
        print("Increase of {0:.2f} from last. Increase count: {1}".format(increase, increaseCount))
        return result
    return False
##    i = 1
##    for x in range(0, 1920, int(1918 / (grid_size - 1))):
##        for y in range(23, 1040, int(1016 / (grid_size - 1))):
##            px = pyautogui.pixel(x, y)
##            print("Pixel {0}: {1}, {2}, {3}".format(i, px[0], px[1], px[2]))
##            i += 1
##            if not isGreyscale(px):
##                return False
##    debounce = True
##    return True

def bringWindowToFront(window_name):
    pyautogui.getWindowsWithTitle(window_name)[0].maximize()
    
def lowDeviation(color):
    colorMax = max(color)
    colorMin = min(color)
    return (colorMax - colorMin) <= dThreshold

def isGreyscale(color):
    global lastRange
    colorRange = max(color) - min(color)
    print("Color range: {0}".format(colorRange))
    result = colorRange <= rThreshold and colorRange != 0 and underThreshold(color)
    lastRange = colorRange
    return result
    # return inRange(color[0], color[1]) and inRange(color[1], color[2]) and underThreshold(color)

def inRange(color1, color2):
    colorMax = color1 + r
    colorMin = color1 - r
    return color2 <= colorMax and color2 >= colorMin

def inRangeRGB(color1, color2):
    return inRange(color1[0], color2[0]) and inRange(color1[1], color2[1]) and inRange(color1[2], color2[2])

def underThreshold(color):
    for i in range(3):
        if color[i] > threshold or color[i] == 0:
            return False
    return True

def bringToFG():
    try:
        win = gw.getWindowsWithTitle('timestop.mov - VLC Media Player')[0]
        roblox = gw.getWindowsWithTitle('Roblox')[0]
        roblox.minimize()
        win.maximize()
    except Exception:
        print("Matching windows not found")
    
while (True):
    if (process_exists("RobloxPlayerBeta.exe")):
        if (isTimestopped()):
            timestop()
