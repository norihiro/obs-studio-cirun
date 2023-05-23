#! /usr/bin/env python3

import os
import subprocess
import pyautogui
from time import sleep
from obsexec import OBSExec
import obsconfig
import desktoprecord
import util

u = util.u
record = None

def run_firsttime():
    global obs, record
    sleep(1)

    util.set_screenshot_prefix('screenshot/01-firsttime-')

    if sys.platform != 'darwin':
        record = desktoprecord.DesktopRecord(filename='desktop-firsttime.mkv')

    # Start OBS Studio
    obs = OBSExec(obsconfig.OBSConfigClean())

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
    run_firsttime();
    configure_websocket_by_ui()
    terminate_firsttime()
