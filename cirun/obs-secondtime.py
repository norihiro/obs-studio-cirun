#! /usr/bin/env python3

import os
import subprocess
import random
import pyautogui
from time import sleep
from obsexec import OBSExec
import obsconfig
import desktoprecord
import util


sleep(1)
u = util.u
screen_size = pyautogui.size()

util.set_screenshot_prefix('screenshot/02-settings-')

record = desktoprecord.DesktopRecord(filename='desktop-secondtime.mkv')

# Start OBS Studio
obs = OBSExec(obsconfig.OBSConfigCopyFromSaved('obs-config-default'))
try:
    util.wait_text('File Edit View Dock Profile Scene Collection Tools Help', timeout=10,
                   ocrfunc=lambda u: util.ocr_topwindow(mode='top', length=200))
except TimeoutError:
    pass

# Configure settings
## Open
print('Opening Settings dialog')
pyautogui.click(screen_size.width/2, screen_size.height/2) # ensure focus
pyautogui.hotkey('alt', 'f')
pyautogui.hotkey('s')
sleep(2)

## Open Advanced
print('Opening Advanced tab')
u.capture()
util.click_verbose(u.find_text('Advanced'))

## Enable autoremux
util.ocr_topwindow()
util.click_verbose(u.find_text('Automatically remux to mp4'))
util.take_screenshot()
pyautogui.hotkey('enter')

## Ensure to close dialog
for i in range(0, 3):
    sleep(1)
    pyautogui.hotkey('esc')

# Open obs-websocket client
cl = obs.get_obsws()

# Set Studio Mode
cl.set_studio_mode_enabled(True)
sleep(1)
util.take_screenshot()

# Set Streaming
cl.send('SetStreamServiceSettings', {
    'streamServiceType': 'rtmp_custom',
    'streamServiceSettings': {
        'server': 'rtmp://localhost/live',
        'key': 'cirun',
        }})

# Create various scources
scenes = set()
for scene in cl.send('GetSceneList').scenes:
    scenes.add(scene['sceneName'])

input_kinds = cl.send('GetInputKindList').input_kinds
print('Available input-kinds are: ' + ' '.join(input_kinds))

def _mouse_move_around_preview():
    geometry = util.current_window_geometry()
    x = int(random.uniform(geometry[0] + 10, (geometry[0] * 2 + geometry[2] * 1) / 3))
    y = int(random.uniform(geometry[1] + 50, (geometry[1] * 3 + geometry[3] * 2) / 5))
    pyautogui.moveTo(x, y)

util.set_screenshot_prefix('screenshot/02-various-source-')

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
            'update_settings': [
                {
                    'outline': True,
                    },
                {
                    'outline': False,
                    'drop_shadow': True,
                    },
                {
                    'drop_shadow': False,
                    },
                ]
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
    cl.send('SetCurrentProgramScene', {'sceneName': sceneName})
    if sceneName == background_source:
        cl.send('StartRecord')
        cl.send('StartStream')
    if 'sleep_after_creation' in source:
        sleep(source['sleep_after_creation'])
    util.take_screenshot()
    if 'update_settings' in source:
        for settings in source['update_settings']:
            name = source['inputName']
            data = {'inputName': name, 'inputSettings': settings}
            print('SetInputSettings %s' % data)
            cl.send('SetInputSettings', data)
            if 'sleep_after_creation' in source:
                sleep(source['sleep_after_creation'])
            util.take_screenshot()
    _mouse_move_around_preview()
    # Open Transform dialog and close
    sleep(0.2); pyautogui.click()
    sleep(0.2); pyautogui.hotkey('ctrl', 'e')
    sleep(0.2); pyautogui.hotkey('esc')
    sleep(0.2); pyautogui.hotkey('esc')

# Switch to the background scene
cl.send('SetCurrentPreviewScene', {'sceneName': background_source})
cl.send('TriggerStudioModeTransition')
cl.send('SetCurrentPreviewScene', {'sceneName': background_source})
sleep(1)

# Terminate OBS
cl.send('StopRecord')
cl.send('StopStream')
cl.base_client.ws.close()
sleep(15) # wait enough to ensure remux has finished.
pyautogui.click(screen_size.width/2, screen_size.height/2)
obs.term()

record.stop()
