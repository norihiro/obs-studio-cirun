import sys
from time import sleep
import unittest
import obstest
import obsplugin
import util


class OBSPTZTest(obstest.OBSTest):
    def setUp(self):
        super().setUp(run=False)

    def test_ptz(self):
        util.set_screenshot_prefix('screenshot/test_ptz-')
        obsplugin.download_install_plugin_macos('glikely/obs-ptz')

        self.obs.run()

        u = util.u
        util.take_screenshot()
        util.ocr_mainmenu()
        util.click_verbose(u.find_text('Docks'))
        util.take_screenshot()
        util.click_verbose(u.find_text('PTZ Controls'))

        sleep(3)
        util.take_screenshot()


# So far, This test works for macOS.
# TODO: Also implement for Ubuntu 22.04.
if sys.platform != 'darwin':
    del OBSPTZTest


if __name__ == '__main__':
    unittest.main()
