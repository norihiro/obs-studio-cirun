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
        self._obsws = None
        if run:
            self.run()

    def run(self):
        self._obsws = None
        if sys.platform == 'linux':
            self.proc_obs = subprocess.Popen(['obs'])
        elif sys.platform == 'darwin':
            self.proc_obs = subprocess.Popen(['open', '-W', 'obs-studio/build_macos/UI/RelWithDebInfo/OBS.app'])
        elif sys.platform == 'win32':
            oldcwd = os.getcwd()
            os.chdir('obs-studio/bin/64bit')
            self.proc_obs = subprocess.Popen(['obs64.exe'])
            os.chdir(oldcwd)
        else:
            raise Exception(f'Not supported platform: f{sys.platform}')
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

    def term_hotkey(self):
        if sys.platform == 'linux':
            pyautogui.hotkey('ctrl', 'q')

        elif sys.platform == 'darwin':
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

        elif sys.platform == 'win32':
            pyautogui.hotkey('esc')
            pyautogui.hotkey('alt', 'f')
            pyautogui.hotkey('x')
            if self._is_terminated():
                return
            pyautogui.hotkey('alt', 'f4')
            sleep(1); pyautogui.hotkey('esc')
            sleep(1); pyautogui.hotkey('esc')

    def term_menu_by_mouse(self):
        if sys.platform == 'darwin':
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

        elif sys.platform == 'win32':
            try:
                util.take_screenshot()
                tt = util.u.find_texts('File Edit View Dock Profile Scene Collection Tools Help')
                if len(tt) and tt[0].confidence > 0.7:
                    loc = tt[0].location
                    cx, cy = loc.center()
                    cy -= loc.y1 - loc.y0
                    pyautogui.click((cx, cy))
                    pyautogui.hotkey('alt', 'f4')
            except:
                pass

    def term_by_sigint(self):
        if sys.platform == 'linux':
            self.proc_obs.send_signal(subprocess.signal.SIGINT)
            if self._is_terminated(timeout=20):
                print('Info: obs was terminated by SIGINT.', flush=True)
                return
            print('Error: failed to wait obs. SIGINT could not terminate obs.', flush=True)

        elif sys.platform == 'darwin':
            ret = os.system(f'killall -INT OBS')
            if ret != 0:
                return
            if self._is_terminated():
                print(f'Info: OBS was terminated by killall -INT', flush=True)
                return
            print('Error: failed to terminate obs by killall -INT.', flush=True)

    def term_by_signal(self):
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

        if sys.platform == 'darwin':
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

        if sys.platform == 'win32':
            try:
                os.system('taskkill.exe /IM obs64.exe')
            except:
                pass


    def term(self):
        try:
            # On Windows, existing connections in obs-websocket somehow block shutdown.
            # Let's close the obsws instance before shutdown.
            if self._obsws:
                self._obsws.base_client.ws.close()
                self._obsws = None
        except:
            pass

        self.config.clear_cache()

        if self._is_terminated(timeout=0):
            return

        self.term_by_sigint()
        if self._is_terminated():
            return

        self.term_hotkey()
        if self._is_terminated():
            return
        print('Warning: Failed to terminate obs using the hotkey. Trying another method...')
        sys.stdout.flush()

        self.term_menu_by_mouse()
        if self._is_terminated():
            return

        self.term_by_signal()
        if self._is_terminated():
            return

        self.proc_obs.kill()
        if self._is_terminated():
            return

        raise Exception('Failed to terminate obs')

    def get_obsws(self, use_cache=True):
        if use_cache:
            try:
                if self._obsws and self._obsws.base_client.ws.connected:
                    self._obsws = None
            except:
                pass

            if self._obsws:
                return self._obsws

        global_cfg = self.config.get_global()
        obsws_pw = global_cfg['OBSWebSocket']['ServerPassword']
        n_retry = 10
        err = None
        while n_retry > 0:
            n_retry -= 1
            try:
                self._obsws = obsws_python.ReqClient(host='localhost', port=4455, password=obsws_pw)
                if sys.platform == 'linux' and n_retry != 9:
                    print(f'Info: Succeeded to connect to obs-websocket after {8 - n_retry} failed attempt(s).')
                    sys.stdout.flush()
                    os.system('ss -tnlp')
                return self._obsws
            except ConnectionRefusedError as e:
                err = e
                if self.proc_obs and self.proc_obs.poll() == None:
                    sleep(3)
                    print(f'Info: Failed to connect to obs-websocket {e=}. {n_retry} more attempt(s).')
                    sys.stdout.flush()
                    if sys.platform == 'linux':
                        os.system('ss -tnlp || sudo apt install -y iproute2 && ss -tnlp')
        raise err

    def get_logfile(self):
        logsdir = self.config.path + '/logs/'
        logs = os.listdir(logsdir)
        if not logs:
            return None
        return logsdir + max(logs)
