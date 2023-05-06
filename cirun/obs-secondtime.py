#! /usr/bin/env python3

import configparser
import os
import subprocess
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
proc_obs = subprocess.Popen(['obs'])
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
## Ensure to close dialog
for i in range(0, 3):
    sleep(1)
    pyautogui.hotkey('esc')

# Configure settings
## Open
u.capture()
workaround_crop_manual(u, y=100)
u.find_text('File').click()
sleep(1)
u.capture()
workaround_crop_manual(u, x=300, y=400)
u.find_text('Settings').click()
sleep(1)

## Open Advanced
u.capture()
workaround_crop_manual(u, x=300, y=500)
u.find_text('Advanced').click()
sleep(1)

## Enable autoremux
u.capture()
workaround_current_window(u)
u.find_text('Automatically remux to mp4').click()
sleep(1)
u.capture()
u.screenshot.save('screenshot/secondtime-02-settings-advanced.png')
pyautogui.hotkey('enter')

## Ensure to close dialog
for i in range(0, 3):
    sleep(1)
    pyautogui.hotkey('esc')

# Start obs-websocket client
cl = obsws.ReqClient(host='localhost', port=4455, password=get_obsws_password())

# Set Studio Mode
cl.set_studio_mode_enabled(True)
sleep(1)
u.capture()
u.screenshot.save('screenshot/secondtime-02-studiomode.png')

# Create various scources
scenes = set()
for scene in cl.send('GetSceneList').scenes:
    scenes.add(scene['sceneName'])

sources = [
        {
            'inputName': 'background',
            'sceneName': 'Background Scene',
            'inputKind': 'color_source_v3',
            'inputSettings': {
                'color': 0xff582416,
                },
            },
        {
            'inputName': 'text',
            'sceneName': 'Scene Text',
            'inputKind': 'text_ft2_source_v2',
            'inputSettings': {
                'text': 'Text Source',
                },
            },
        ]

background_source = sources[0]['sceneName']

for source in sources:
    sceneName = source['sceneName']
    if not sceneName in scenes:
        cl.send('CreateScene', {'sceneName': sceneName})
        scenes.add(sceneName)
    if sceneName != background_source:
        cl.send('CreateSceneItem', {'sceneName': sceneName, 'sourceName': background_source})
    cl.send('CreateInput', source)
    cl.send('SetCurrentPreviewScene', {'sceneName': sceneName})
    cl.send('TriggerStudioModeTransition')
    if sceneName == background_source:
        cl.send('StartRecord')
    sleep(2)

flg_cleanup = False
if flg_cleanup:
    for source in sources:
        sceneName = source['sceneName']
        if sceneName in scenes:
            cl.send('RemoveScene', {'sceneName': sceneName})
            scenes.remove(sceneName)

# Exit OBS
cl.send('StopRecord')
sleep(1)
pyautogui.click(screen_size.width/2, screen_size.height/2)
pyautogui.hotkey('ctrl', 'q')
sleep(2)
proc_obs.send_signal(subprocess.signal.SIGINT)
proc_obs.communicate()
