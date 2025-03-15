import pkg_resources, subprocess, sys

required  = {'pyautogui', "pywin32", "keyboard", "opencv-python"}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing   = required - installed

if missing:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])

from pyautogui import *
import pyautogui
import keyboard
import time
import random

def click(x, y):
    pyautogui.click(x, y)

while keyboard.is_pressed('q') == False:
    flag = 0
    pic = pyautogui.screenshot(region=(433, 248, 1428-433, 886-248))
    width, height = pic.size
    
    for x in range(0, width, 10):
        for y in range(0, height, 10):
            r, g, b = pic.getpixel((x, y))
            if r == 240:
                click(x + 433, y + 248)
                time.sleep(0.05)
                print(f"({x+433}, {y+248}) is clicked")
                flag = 1
                break
        if flag == 1:
            break