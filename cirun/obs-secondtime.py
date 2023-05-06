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
u.find_text('Tools').click()
sleep(1)
u.capture()
u.find_text('WebSocket Server Settings').click()
sleep(1)

## Enable obs-websocket
u.find_text('Enable WebSocket server').click()
sleep(1)

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
u.find_text('Settings', location_hint=(0.9, 0.9, 0.3)).click() # located at bottom right
sleep(2)

## Open Advanced
u.capture()
u.find_text('Advanced').click()
sleep(1)

## Enable autoremux
u.capture()
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
