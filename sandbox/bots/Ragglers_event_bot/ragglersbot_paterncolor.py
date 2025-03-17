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
import win32api, win32con
import os
import cv2
import numpy as np

# Click function using win32api
def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

# OpenCV-based image matching function
def match_image_on_screen(template_path, threshold=0.8):
    try:
        # Take a screenshot of the screen
        screenshot = pyautogui.screenshot()
        screen_np = np.array(screenshot)
        screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_BGR2GRAY)

        # Load the template image
        template = cv2.imread(template_path, 0)  # Load in grayscale
        if template is None:
            print(f"Error: Could not load image from {template_path}")
            return None

        w, h = template.shape[::-1]

        # Perform template matching
        result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)

        # Return the first match if found
        for pt in zip(*loc[::-1]):
            print(f"Match found at: {pt}")
            return pt[0], pt[1]

    except Exception as e:
        print(f"Error during image matching: {e}")
    return None

# Path to the template image
cat_png = os.path.join(os.path.dirname(__file__), 'cat.png')

while not keyboard.is_pressed('q'):
    # Match the image on the screen
    match = match_image_on_screen(cat_png, threshold=0.95)
    if match:
        print(f"{cat_png} is found at {match}")
        x, y = match
        flag = 0

        # Take a screenshot of the defined region
        pic = pyautogui.screenshot(region=(433, 248, 1428 - 433, 886 - 248))
        width, height = pic.size

        for x_offset in range(0, width, 10):
            for y_offset in range(0, height, 10):
                r, g, b = pic.getpixel((x_offset, y_offset))
                if r == 232 and g == 198:  # Condition for color matching
                    click(x_offset + 433, y_offset + 248)
                    time.sleep(0.05)
                    print(f"({x_offset + 433}, {y_offset + 248}) is clicked")
                    flag = 1
                    break
            if flag == 1:
                break
    else:
        print("Image not found.")
