'''
This module provides a functionality to run obs-studio to test it.
'''

import os
import sys
import subprocess
from time import sleep
import pyautogui
import obsws_python
import util

class OBSExec:
    def __init__(self, config=None, run=True):
        if not config:
            import obsconfig
            config = obsconfig.OBSConfig()
        self.config = config
        self.proc_obs = None
        if run:
            self.run()

    def run(self):
        if sys.platform == 'linux':
            self.proc_obs = subprocess.Popen(['obs'])
        elif sys.platform == 'darwin':
            os.system('open obs-studio/build_x86_64/UI/RelWithDebInfo/OBS.app')
        sleep(5)

    def term(self):
        pyautogui.hotkey('ctrl', 'q')
        self.config.clear_cache()
        sleep(4)
        if sys.platform == 'linux':
            self.proc_obs.send_signal(subprocess.signal.SIGINT)
            try:
                self.proc_obs.communicate(timeout=20)
            except subprocess.TimeoutExpired:
                print('Error: failed to wait obs. SIGINT could not terminate obs.')
            self.proc_obs.send_signal(subprocess.signal.SIGKILL)
            try:
                self.proc_obs.communicate(timeout=20)
            except subprocess.TimeoutExpired:
                print('Error: failed to wait obs though SIGKILL was sent.')
        elif sys.platform == 'darwin':
            try:
                util.u.ocr(crop=(0, 0, 216, 40))
                util.click_verbose(util.u.find_text('OBS Studio'))
                util.u.ocr(crop=(0, 0, 480, 540))
                util.take_screenshot()
                util.click_verbose(util.u.find_text('Exit'))
            except:
                print('Error: failed to open menu to exit')
                util.take_screenshot()
            for cmd in ('killall -INT', 'killall'):
                retry = 2
                while retry > 0:
                    ret = os.system(f'{cmd} OBS')
                    if ret != 0:
                        return
                    retry -= 1
                    sleep(10)

    def get_obsws(self):
        global_cfg = self.config.get_global()
        obsws_pw = global_cfg['OBSWebSocket']['ServerPassword']
        return obsws_python.ReqClient(host='localhost', port=4455, password=obsws_pw)
