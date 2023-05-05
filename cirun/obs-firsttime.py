#! /usr/bin/env python3

import os
import pyautogui
from untriseptium import Untriseptium
from time import sleep

u = Untriseptium()
screen_size = pyautogui.size()

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
