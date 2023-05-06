#! /usr/bin/env python3

import os
import subprocess
import pyautogui
from untriseptium import Untriseptium
from time import sleep

flg_x11grab = True

sleep(1)
u = Untriseptium()
screen_size = pyautogui.size()

if flg_x11grab:
    proc_ffmpeg = subprocess.Popen([
        'ffmpeg',
        '-loglevel', 'error',
        '-video_size', f'{screen_size.width}x{screen_size.height}',
        '-framerate', '5',
        '-f', 'x11grab',
        '-i', os.environ['DISPLAY'],
        '-y', 'desktop-firsttime.mkv'
        ], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Start OBS Studio
os.system('rm -rf $HOME/.config/obs-studio')
os.system('obs &>/dev/null &')
sleep(5)
u.capture()
u.screenshot.save('screenshot/firsttime-0.png')

# Continue the wizard
tt = u.find_texts('Optimize just for recording, I will not be streaming')
tt[0].click()
u.capture()
u.screenshot.save('screenshot/firsttime-1.png')
pyautogui.hotkey('enter') # Next
sleep(2)
u.capture()
u.screenshot.save('screenshot/firsttime-2.png')
pyautogui.hotkey('enter') # Next
sleep(2)
u.capture()
u.screenshot.save('screenshot/firsttime-3.png')
while True:
    sleep(2)
    u.capture()
    t = u.find_text('Testing complete')
    if t.confidence > 0.9:
        break
u.screenshot.save('screenshot/firsttime-4.png')
pyautogui.hotkey('enter') # Apply Settings
pyautogui.click(screen_size.width/2, screen_size.height/2)
u.capture()
u.screenshot.save('screenshot/firsttime-5.png')
pyautogui.hotkey('ctrl', 'q')
sleep(1)

if flg_x11grab:
    proc_ffmpeg.stdin.write('q'.encode())
    proc_ffmpeg.stdin.flush()
    proc_ffmpeg.stdin.close()
    proc_ffmpeg.communicate()

sleep(1)
