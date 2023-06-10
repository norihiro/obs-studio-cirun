import psutil
import sys
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


class OBSTest(unittest.TestCase):
    def setUp(self, config_name='obs-config-default', run=True):
        name = self.id().split('.')[-1]
        util.set_screenshot_prefix(f'screenshot/{name}-')
        if _is_obs_running():
            raise Exception('OBS has already been running')
        self.obs = OBSExec(OBSConfigCopyFromSaved(config_name), run=run)
        if run:
            if sys.platform == 'linux':
                util.wait_text('File Edit View Dock Profile Scene Collection Tools Help', timeout=10,
                               ocrfunc=lambda u: util.ocr_topwindow(mode='top', length=200))
            elif sys.platform == 'darwin':
                util.wait_text('OBS Studio File Edit View Dock Profile Scene Collection Tools Help', timeout=10,
                               ocrfunc=lambda u: u.ocr(crop=(0, 0, u.screenshot.width, 40)) )

    def tearDown(self):
        self.obs.term()
        self.obs.config.move_logs()
        util.macos_check_fault()
        if _is_obs_running():
            raise Exception('OBS did not exit')
