#! /usr/bin/env python3

import configparser
import os
import pyautogui
from untriseptium import Untriseptium
from time import sleep
import obsws_python as obsws


sleep(1)
u = Untriseptium()
screen_size = pyautogui.size()


def workaround_crop_manual(u, x=None, y=None):
    if not u.screenshot:
        u.capture()
    if not x:
        x = screen_size.width
    if not y:
        y = screen_size.height
    u.screenshot = u.screenshot.crop((0, 0, x, y))
    u.ocr()


def workaround_current_window(u):
    import subprocess
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
    workaround_crop_manual(u, x0+x1, y0+y1)


def get_obsws_password():
    config = configparser.ConfigParser()
    home = os.environ['HOME']
    config.read(home + '/.config/obs-studio/global.ini')
    return config['OBSWebSocket']['ServerPassword']


# Start OBS Studio
os.system('obs &>/dev/null &')
sleep(5)

# Configure obs-websocket
## Open obs-websocket dialog
u.capture()
workaround_crop_manual(u, y=50)
u.find_text('Tools').click()
u.capture()
workaround_current_window(u)
workaround_crop_manual(u, y=250)
u.find_text('WebSocket Server Settings').click()

## Enable obs-websocket
workaround_current_window(u)
u.find_text('Enable WebSocket server').click()

u.capture()
u.screenshot.save('screenshot/secondtime-01-obswebsocket.png')
pyautogui.hotkey('enter')
sleep(1)
u.capture()
u.screenshot.save('screenshot/secondtime-01-obswebsocket-end.png')

# Start obs-websocket client
cl = obsws.ReqClient(host='localhost', port=4455, password=get_obsws_password())
print(cl.get_version())

# Set Studio Mode
cl.set_studio_mode_enabled(True)
sleep(1)
u.capture()
u.screenshot.save('screenshot/secondtime-02-studiomode.png')

# Exit OBS
pyautogui.click(screen_size.width/2, screen_size.height/2)
pyautogui.hotkey('ctrl', 'q')
sleep(2)
