#! /usr/bin/env python3

import configparser
import os
import subprocess
import pyautogui
from untriseptium import Untriseptium
from time import sleep
import obsws_python as obsws
from util import *


flg_x11grab = True


sleep(1)
u = Untriseptium()
u.ocrengine.ocr_split_height = 32
screen_size = pyautogui.size()


def get_obsws_password():
    config = configparser.ConfigParser()
    home = os.environ['HOME']
    config.read(home + '/.config/obs-studio/global.ini')
    return config['OBSWebSocket']['ServerPassword']

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

def click_verbose(t):
    print(f'Clicking text={t.text} location={t.location} confidence={t.confidence}')
    t.click()
    sleep(0.2)

if flg_x11grab:
    proc_ffmpeg = subprocess.Popen([
        'ffmpeg',
        '-loglevel', 'error',
        '-video_size', f'{screen_size.width}x{screen_size.height}',
        '-framerate', '5',
        '-f', 'x11grab',
        '-i', os.environ['DISPLAY'],
        '-x264-params', 'keyint=10:min-keyint=5',
        '-y', 'desktop-secondtime.mkv'
        ], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Start OBS Studio
proc_obs = subprocess.Popen(['obs'])
sleep(5)

# Configure obs-websocket
## Open obs-websocket dialog
print('Opening Tools -> WebSocket Server Settings...')
ocr_topwindow(mode='top', length=100)
u.screenshot.save('screenshot/secondtime-01-init.png')
click_verbose(u.find_text('Tools'))
ocr_topwindow(mode='top', length=500)
u.screenshot.save('screenshot/secondtime-01-menu-tools.png')
click_verbose(u.find_text('WebSocket Server Settings'))

## Enable obs-websocket
click_verbose(u.find_text('Plugin Settings')) # click somewhere to raise window
ocr_topwindow()
click_verbose(u.find_text('Enable WebSocket server'))

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
print('Opening Settings dialog')
pyautogui.click(screen_size.width/2, screen_size.height/2) # ensure focus
pyautogui.hotkey('alt', 'f')
pyautogui.hotkey('s')
sleep(2)

## Open Advanced
print('Opening Advanced tab')
u.capture()
click_verbose(u.find_text('Advanced'))

## Enable autoremux
ocr_topwindow()
click_verbose(u.find_text('Automatically remux to mp4'))
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
        {
            'inputName': 'images',
            'sceneName': 'Scene Images',
            'inputKind': 'slideshow',
            'inputSettings': {
                'files': [
                    {
                        'value': os.getcwd() + '/screenshot',
                        'selected': False,
                        'hidden': False,
                        },
                    ],
                },
            },
        {
            'inputName': 'browser',
            'sceneName': 'Scene Browser',
            'inputKind': 'browser_source',
            'inputSettings': {
                'url': 'https://www.youtube.com/watch?v=ghuB0ozPttI&list=UULFp_UXGmCCIRaX5pyFljICoQ',
                'reroute_audio': False,
                },
            'sleep_after_creation': 5,
            'update_settings': [
                {
                    'reroute_audio': True
                    },
                {
                    'reroute_audio': False
                    },
                ]
            },
        {
            'inputName': 'xshm',
            'sceneName': 'Scene Desktop',
            'inputKind': 'xshm_input',
            'inputSettings': {
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
    cl.send('SetCurrentProgramScene', {'sceneName': sceneName})
    if sceneName == background_source:
        cl.send('StartRecord')
        cl.send('StartStream')
    if 'sleep_after_creation' in source:
        sleep(source['sleep_after_creation'])
    else:
        sleep(2)
    if 'update_settings' in source:
        for settings in source['update_settings']:
            name = source['inputName']
            data = {'inputName': name, 'inputSettings': settings}
            print('SetInputSettings %s' % data)
            cl.send('SetInputSettings', data)
            if 'sleep_after_creation' in source:
                sleep(source['sleep_after_creation'])
            else:
                sleep(2)

flg_cleanup = False
if flg_cleanup:
    for source in sources:
        sceneName = source['sceneName']
        if sceneName in scenes:
            cl.send('RemoveScene', {'sceneName': sceneName})
            scenes.remove(sceneName)

# Open projectors
def _close_projector():
    sleep(1)
    pyautogui.rightClick(current_window_center())
    sleep(0.5)
    pyautogui.hotkey('up')
    sleep(0.5)
    pyautogui.hotkey('enter')

cl.send('OpenSourceProjector', {'sourceName': background_source})
_close_projector()
cl.send('OpenVideoMixProjector', {'videoMixType': 'OBS_WEBSOCKET_VIDEO_MIX_TYPE_MULTIVIEW', 'monitorIndex': 0})
## click `Always On Top`
sleep(1)
pyautogui.rightClick()
sleep(0.2)
pyautogui.hotkey('up')
pyautogui.hotkey('up')
sleep(1.0)
pyautogui.hotkey('enter')
## click a source to make transition
pyautogui.click((int(screen_size[0] * 0.6), int(screen_size[1] * 0.6)))
sleep(0.1)
pyautogui.doubleClick((int(screen_size[0] * 0.3), int(screen_size[1] * 0.6)))
sleep(0.2)
_close_projector()
cl.send('OpenVideoMixProjector', {'videoMixType': 'OBS_WEBSOCKET_VIDEO_MIX_TYPE_PROGRAM'})
_close_projector()
cl.send('OpenVideoMixProjector', {'videoMixType': 'OBS_WEBSOCKET_VIDEO_MIX_TYPE_PREVIEW'})
_close_projector()

# Switch to the background scene
cl.send('SetCurrentPreviewScene', {'sceneName': background_source})
cl.send('TriggerStudioModeTransition')
cl.send('SetCurrentPreviewScene', {'sceneName': background_source})
sleep(1)

# Upload the log file
print('Uploading the log file...')
u.capture()
click_verbose(u.find_text('Help'))
ocr_topwindow(mode='top', length=500)
click_verbose(u.find_text('Log Files'))
ocr_topwindow(mode='top', length=500)
click_verbose(u.find_text('Upload Current Log File'))
sleep(5)
pyautogui.hotkey('enter')

# Exit OBS
cl.send('StopRecord')
cl.send('StopStream')
sleep(5)
pyautogui.click(screen_size.width/2, screen_size.height/2)
pyautogui.hotkey('ctrl', 'q')
sleep(2)
proc_obs.send_signal(subprocess.signal.SIGINT)
try:
    proc_obs.communicate(timeout=10)
except subprocess.TimeoutExpired:
    print('Error: failed to wait obs.')

if flg_x11grab:
    proc_ffmpeg.stdin.write('q'.encode())
    proc_ffmpeg.stdin.flush()
    proc_ffmpeg.stdin.close()
    proc_ffmpeg.communicate()

sleep(1)
