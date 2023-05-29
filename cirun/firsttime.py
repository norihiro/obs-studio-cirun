#! /usr/bin/env python3

import os
import subprocess
import sys
import pyautogui
from time import sleep
from obsexec import OBSExec
import obsconfig
import obsplugin
import desktoprecord
import util

u = util.u
record = None

def _location_width(t):
    return t.location.x1 - t.location.x0


def clean_desktop():
    '''
    Close windows and popups already displayed at the startup on GitHub Actions.
    '''
    if sys.platform == 'darwin':
        util.set_screenshot_prefix('screenshot/01-00-prepare-')
        util.take_screenshot()
        u.ocr(crop=(u.screenshot.width - 400, 24, u.screenshot.width, 180))
        tt = u.find_texts('New software is ready to be installed.')
        if len(tt) == 0 or tt[0].confidence < 0.8:
            return
        util.click_verbose(tt[0])
        util.take_screenshot()
        pyautogui.hotkey('command', 'q')
        util.take_screenshot()
        pyautogui.hotkey('command', 'q')
        util.take_screenshot()

    elif sys.platform == 'win32':
        util.set_screenshot_prefix('screenshot/01-00-prepare-')
        util.take_screenshot()
        pyautogui.hotkey('win', 'down')
        util.take_screenshot()
        pyautogui.hotkey('win', 'down')
        util.take_screenshot()


def _app_permissions_macos():
    sleep(3)
    util.take_screenshot()
    util.wait_text('Review App Permissions', timeout=45)

    # Sometimes `wait_text` returns while the dialog is still appearing and it's transparent. Wait more time.
    sleep(5)
    u.capture()

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


def _new_update_available():
    sleep(3)
    try:
        time_passed = 0
        timeout = 10
        while True:
            sleep(1)
            time_passed += 1
            u.capture()
            tt_update = u.find_texts('Update Now Remind me Later Skip Version')
            if len(tt_update) > 0 and tt_update[0].confidence > 0.8:
                util.click_verbose(tt_update[0])
            tt_firsttime = u.find_texts('Specify what you want to use the program for')
            if len(tt_update) > 0 and tt_update[0].confidence > 0.8:
                return
            if time_passed >= timeout:
                s_bestmatch = f'current best match is "{tt[0].text}"' if len(tt) else 'no matching text'
                raise TimeoutError(f'Cannot find "{text}" {s_bestmatch}')
    except:
        return


def run_firsttime():
    global obs, record
    sleep(1)

    if sys.platform == 'linux':
        record = desktoprecord.DesktopRecord(filename='desktop-firsttime.mkv')

    cfg = obsconfig.OBSConfigClean()

    try:
        obsplugin.download_install_plugin('norihiro/obs-shutdown-plugin')
    except:
        import traceback
        traceback.print_exc(file=sys.stdout)

    # Start OBS Studio
    obs = OBSExec(cfg)

    # App Permission
    if sys.platform == 'darwin':
        util.set_screenshot_prefix('screenshot/01-01-permissions-')
        _app_permissions_macos()

    # New update
    if sys.platform == 'win32':
        _new_update_available()

    util.set_screenshot_prefix('screenshot/01-10-autoconf-')

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
    util.set_screenshot_prefix('screenshot/01-20-websocket-')
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
        clean_desktop()
    except:
        import traceback
        traceback.print_exc(file=sys.stdout)
        util.take_screenshot(capture=False)

    try:
        run_firsttime()
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
