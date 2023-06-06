import sys
from time import sleep
import unittest
import obstest
import obsplugin
import util


class OBSPTZTest(obstest.OBSTest):
    def setUp(self):
        super().setUp(run=False)

    def tearDown(self):
        super().tearDown()
        obsplugin.uninstall_all_plugins()

    def test_ptz(self):
        util.set_screenshot_prefix('screenshot/test_ptz-')
        obsplugin.download_install_plugin('glikely/obs-ptz')

        self.obs.run()

        u = util.u
        util.take_screenshot()
        util.ocr_mainmenu()
        t = util.click_verbose(u.find_text('Docks'))
        util.take_screenshot()
        util.ocr_verbose(crop=util.expand_locator(t, (120, 0, 120, 360)))
        util.click_verbose(u.find_text('PTZ Controls'))

        sleep(3)
        util.take_screenshot()


if __name__ == '__main__':
    unittest.main()
