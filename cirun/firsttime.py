#! /usr/bin/env python3

import os
import subprocess
import sys
import pyautogui
from time import sleep
from obsexec import OBSExec
import obsconfig
import desktoprecord
import util

u = util.u
record = None

def _location_width(t):
    return t.location.x1 - t.location.x0

def _app_permissions_macos():
    util.take_screenshot()
    util.wait_text('Review App Permissions', timeout=45)

    t_camera_desc = u.find_text('This permission is needed in order to capture content from a webcam or capture card.')
    t_microphone_desc = u.find_text('OBS requires this permission if you want to capture your microphone.')
    t_hotkeys_desc = u.find_text('For keyboard shortcuts (hotkeys) to work while other apps are focused, please enable this permission.')
    w_est = max(_location_width(t_camera_desc), _location_width(t_microphone_desc), _location_width(t_hotkeys_desc)) * 2

    # Microphone
    x0 = t_microphone_desc.location.x0
    y0 = t_microphone_desc.location.y1
    x1 = x0 + w_est
    y1 = t_hotkeys_desc.location.y0
    u.ocr(crop=(x0, y0, x1, y1))
    util.click_verbose(u.find_text('Request Access'))
    util.take_screenshot()
    # FIXME: Untriseptium cannot find `OK` button. Crop left and right to make OCR success.
    screen_size = pyautogui.size()
    util.wait_text('OBS needs to access the microphone', timeout=6, ocrfunc=\
            lambda u: u.ocr(crop=(screen_size.width/2-125, 0, screen_size.width/2+125, screen_size.height)) )
    util.click_verbose(u.find_text('OK'))
    util.take_screenshot()

    util.click_verbose(u.find_text('Continue'))

def run_firsttime():
    global obs, record
    sleep(1)

    util.set_screenshot_prefix('screenshot/01-firsttime-')

    if sys.platform != 'darwin':
        record = desktoprecord.DesktopRecord(filename='desktop-firsttime.mkv')

    # Start OBS Studio
    obs = OBSExec(obsconfig.OBSConfigClean())

    # App Permission
    if sys.platform == 'darwin':
        _app_permissions_macos()

    util.wait_text('Specify what you want to use the program for', timeout=5)
    util.take_screenshot()

    # Continue the wizard
    util.click_verbose(u.find_text('Optimize just for recording, I will not be streaming'))
    util.take_screenshot()
    pyautogui.hotkey('enter') # Next
    util.take_screenshot()

    pyautogui.hotkey('enter') # Next
    sleep(2)
    util.take_screenshot()

    util.wait_text('Testing complete', timeout=300)
    util.take_screenshot()

    pyautogui.hotkey('enter') # Apply Settings
    screen_size = pyautogui.size()
    pyautogui.click(screen_size.width/2, screen_size.height/2)
    util.take_screenshot()

def configure_websocket_by_ui():
    # Open obs-websocket dialog
    util.set_screenshot_prefix('screenshot/01-websocket-')
    util.take_screenshot()
    util.ocr_topwindow(mode='top', length=100)
    util.click_verbose(u.find_text('Tools'))
    util.take_screenshot()
    util.ocr_topwindow(mode='top', length=500)
    util.click_verbose(u.find_text('WebSocket Server Settings'))
    util.take_screenshot()

    ## Enable obs-websocket
    util.click_verbose(u.find_text('Plugin Settings')) # click somewhere to raise window
    util.take_screenshot()
    util.ocr_topwindow()
    util.click_verbose(u.find_text('Enable WebSocket server'))
    util.take_screenshot()

    pyautogui.hotkey('enter')
    util.take_screenshot()

def terminate_firsttime():
    global obs, record
    obs.term()
    if record:
        record.stop()

    sleep(1)

    obs.config.save('obs-config-firsttime')

    obsconfig.append_preset(obs.config)

    profile = obs.config.get_profile()
    profile['Video']['BaseCX'] = '1280'
    profile['Video']['BaseCY'] = '720'
    profile['Video']['OutputCX'] = '1280'
    profile['Video']['OutputCY'] = '720'
    profile.save()

    obs.config.save('obs-config-default')

if __name__ == '__main__':
    ret = 0
    try:
        run_firsttime();
        if sys.platform == 'linux':
            # TODO: Run in a separated test case
            configure_websocket_by_ui()
    except:
        ret = 1
        import traceback
        traceback.print_exc(file=sys.stdout)
        util.take_screenshot(capture=False)
    try:
        terminate_firsttime()
    except:
        ret = 2
        import traceback
        traceback.print_exc()
        util.take_screenshot()
    if ret:
        sys.exit(ret)
