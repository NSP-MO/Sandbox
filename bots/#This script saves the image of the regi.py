#This script saves the image of the region 660,350,600,400 as savedimage.png in the path "C:\Users\Antec\Desktop\Tutorial\savedimage.png"

import pyautogui

im1 = pyautogui.screenshot(region=(433, 248, 1428-433, 886-248))
im1.save(r"./savedimage.png")