import psutil
import sys
from time import sleep
import unittest
from obsexec import OBSExec
from obsconfig import OBSConfigCopyFromSaved
import util


def _is_obs_running():
    for p in psutil.process_iter():
        if sys.platform == 'linux' and p.name() == 'obs':
            return True
        if sys.platform == 'darwin' and p.name() == 'OBS':
            return True
        if sys.platform == 'win32' and p.name().lower() == 'obs64.exe':
            return True
    return False


def ensure_not_running():
    if _is_obs_running():
        print('OBS has already been running. Killing it...')
        OBSExec.killall_obs()
    if _is_obs_running():
        raise Exception('OBS is still running though attempted to terminate.')


class OBSTest(unittest.TestCase):
    def setUp(self, config_name='obs-config-default', run=True):
        if _is_obs_running():
            print('OBS has already been running. Killing it...')
            OBSExec.killall_obs()
        name = self.id().split('.')[-1]
        if name[:5] == 'test_':
            name = name[5:]
        util.set_screenshot_prefix(f'screenshot/{name}-')
        if _is_obs_running():
            raise Exception('OBS has already been running')
        self.obs = OBSExec(OBSConfigCopyFromSaved(config_name), run=run)
        if run:
            if sys.platform == 'linux':
                util.wait_text('File Edit View Dock Profile Scene Collection Tools Help', timeout=10,
                               ocrfunc=lambda u: util.ocr_topwindow(mode='top', length=200))
            elif sys.platform == 'darwin':
                util.wait_text('OBS File Edit View Dock Profile Scene Collection Tools Help', timeout=10,
                               ocrfunc=lambda u: u.ocr(crop=(0, 0, u.screenshot.width, 40)) )

    def tearDown(self):
        self.obs.term()

        try:
            wait_memleak_sec = 30
            while not self._log_has_memleak_count():
                print(f'Warning: Cannot find "Number of memory leaks" in the log "{self.obs.get_logfile()}". Waiting...', flush=True)
                sleep(5)
                wait_memleak_sec -= 5
                util.macos_check_fault()
                if wait_memleak_sec <= 0:
                    break
        except TypeError:
            pass

        self.obs.config.move_logs()
        if _is_obs_running():
            raise Exception('OBS did not exit')

    def _log_has_memleak_count(self):
        with open(self.obs.get_logfile()) as f:
            lines = f.read().split('\n')
        for l in lines[-2:]:
            if 'Number of memory leaks:' in l:
                return True
        return False
