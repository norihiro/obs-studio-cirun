import os
import random
import sys
from time import sleep
import unittest
import pyautogui
import obstest
import util


class OBSLogTest(obstest.OBSTest):
    def test_upload_current_log(self):
        u = util.u
        if sys.platform == 'darwin':
            ocr_topwindow = util.ocr_screen
        else:
            ocr_topwindow = util.ocr_topwindow
        util.set_screenshot_prefix('screenshot/test_upload_current_log-')
        util.click_verbose(u.find_text('Help'))
        util.take_screenshot()
        ocr_topwindow(mode='top', length=500)
        util.click_verbose(u.find_text('Log Files'))
        util.take_screenshot()
        ocr_topwindow(mode='top', length=500)
        util.click_verbose(u.find_text('Upload Current Log File'))
        util.take_screenshot()
        sleep(4)
        util.take_screenshot()
        pyautogui.hotkey('enter')
        util.take_screenshot()


if __name__ == '__main__':
    unittest.main()
