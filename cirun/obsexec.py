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
            self.proc_obs = subprocess.Popen(['open', '-W', 'obs-studio/build_x86_64/UI/RelWithDebInfo/OBS.app'])
        sleep(5)

    def _is_terminated(self, timeout=10):
        if not self.proc_obs:
            return True
        try:
            self.proc_obs.communicate(timeout=timeout)
            self.proc_obs = None
            return True
        except subprocess.TimeoutExpired:
            return False

    def term(self):
        self.config.clear_cache()

        if sys.platform != 'darwin':
            pyautogui.hotkey('ctrl', 'q')
            if self._is_terminated():
                return
            print('Warning: Failed to terminate obs using the hotkey. Trying another method...')
            sys.stdout.flush()
        else:
            for i in range(1, 6):
                pyautogui.hotkey('command', 'w')
                sleep(1)
                pyautogui.hotkey('command', 'q')
                if self._is_terminated():
                    if i == 1:
                        ith = '1st'
                    elif i == 2:
                        ith = '2nd'
                    elif i == 3:
                        ith = '3rd'
                    else:
                        ith = f'{i}th'
                    print(f'Info: OBS was terminated by {ith} command-W hotkey.')
                    return
            print('Warning: Failed to terminate obs using the hotkey. Trying another method...')
            sys.stdout.flush()

        if sys.platform == 'linux':
            self.proc_obs.send_signal(subprocess.signal.SIGINT)
            if self._is_terminated(timeout=20):
                print('Info: obs was terminated by SIGINT.')
                sys.stdout.flush()
                return
            print('Error: failed to wait obs. SIGINT could not terminate obs.')
            sys.stdout.flush()
            self.proc_obs.send_signal(subprocess.signal.SIGKILL)
            if self._is_terminated(timeout=20):
                print('Warning: obs was terminated by SIGKILL.')
                sys.stdout.flush()
                return
            print('Error: failed to wait obs though SIGKILL was sent.')
            sys.stdout.flush()

        elif sys.platform == 'darwin':
            try:
                util.u.ocr(crop=(0, 0, 216, 40))
                util.click_verbose(util.u.find_text('OBS Studio'))
                util.u.ocr(crop=(0, 0, 480, 540))
                util.take_screenshot()
                util.click_verbose(util.u.find_text('Quit OBS Studio'))
            except:
                print('Warning: failed to open menu to exit')
                sys.stdout.flush()
                util.take_screenshot()
            if self._is_terminated():
                return

            for cmd in ('killall -INT', 'killall'):
                retry = 2
                while retry > 0:
                    ret = os.system(f'{cmd} OBS')
                    if ret != 0:
                        return
                    retry -= 1
                    if self._is_terminated():
                        print(f'Info: OBS was terminated by {cmd}')
                        sys.stdout.flush()
                        return

        raise Exception('Failed to terminate obs')

    def get_obsws(self):
        global_cfg = self.config.get_global()
        obsws_pw = global_cfg['OBSWebSocket']['ServerPassword']
        n_retry = 5
        err = None
        while n_retry > 0:
            n_retry -= 1
            try:
                return obsws_python.ReqClient(host='localhost', port=4455, password=obsws_pw)
            except ConnectionRefusedError as e:
                err = e
                if self.proc_obs and self.proc_obs.poll() == None:
                    sleep(1)
                    print(f'Info: Failed to connect to obs-websocket {e=}. {n_retry} more attempt(s).')
                    if sys.platform == 'linux':
                        os.system('ss -tnlp || sudo apt install -y iproute2 && ss -tnlp')
                    sys.stdout.flush()
        raise err
