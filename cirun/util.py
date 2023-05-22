import os
import subprocess
import sys
from time import sleep
from untriseptium import Untriseptium


def current_window_geometry():
    if sys.platform == 'darwin':
        import pygetwindow as gw
        a = gw.getActiveWindow()
        x0 = a.left
        y0 = a.top
        x1 = a.width
        y1 = a.height
    elif sys.platform == 'linux':
        s = subprocess.run(['xdotool', 'getwindowfocus', 'getwindowgeometry'], capture_output=True)
        for line in s.stdout.decode().split('\n'):
            line = line.strip().split(' ')
            if len(line) >= 2 and line[0] == 'Position:':
                x0, y0 = line[1].split(',')
            elif len(line) >= 2 and line[0] == 'Geometry:':
                x1, y1 = line[1].split('x')

    x0 = int(x0)
    y0 = int(y0)
    y1 = int(y1)
    x1 = int(x1)
    return (x0, y0, x0+x1, y0+y1)


def current_window_center():
    loc = current_window_geometry()
    return (int((loc[0] + loc[2]) / 2), int((loc[1] + loc[3]) / 2))


def wait_text(text, confidence_threshold=0.9, sleep_each=1, timeout=None, ocrfunc=None):
    '''
    Waits until the specified text appears on the screen.
    text - Expected text that will apear on the screen.
    '''
    time_passed = 0
    while True:
        sleep(sleep_each)
        time_passed += sleep_each
        u.capture()
        if ocrfunc:
            ocrfunc(u)
        tt = u.find_texts(text)
        if len(tt) > 0 and tt[0].confidence > confidence_threshold:
            break
        if timeout and time_passed >= timeout:
            raise TimeoutError


def click_verbose(t):
    print(f'Clicking text="{t.text}" location={t.location} confidence={t.confidence}')
    sys.stdout.flush()
    t.click()
    sleep(0.2)


def ocr_topwindow(mode=None, length=0, ratio=-1):
    sleep(0.1)
    u.capture()
    geometry = current_window_geometry()
    if ratio > 0 and (mode=='left' or mode=='right'):
        length = int((geometry[2] - geometry[0]) * ratio)
    elif ratio > 0 and (mode=='top' or mode=='bottom'):
        length = int((geometry[3] - geometry[1]) * ratio)
    if mode=='left':
        geometry = (geometry[0], geometry[1], min(geometry[0] + length, geometry[2]), geometry[3])
    elif mode=='top':
        geometry = (geometry[0], geometry[1], geometry[2], min(geometry[1] + length, geometry[3]))
    elif mode=='right':
        geometry = (min(geometry[2] - length, geometry[0]), geometry[1], geometry[2], geometry[3])
    elif mode=='bottom':
        geometry = (geometry[0], min(geometry[3] - length, geometry[1]), geometry[2], geometry[3])
    u.ocr(crop=geometry)


_screenshot_prefix = 'screenshot/screenshot-'
_screenshot_index = 0
u = Untriseptium()


def set_screenshot_prefix(name):
    global _screenshot_prefix
    global _screenshot_index
    _screenshot_prefix = name
    _screenshot_index = 0
    os.makedirs(os.path.dirname(name), exist_ok=True)


def take_screenshot():
    global _screenshot_prefix
    global _screenshot_index
    sleep(1)
    u.capture()
    u.screenshot.save(f'{_screenshot_prefix}{_screenshot_index:02d}.png')
    _screenshot_index += 1
