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
        t = util.click_verbose(u.find_text('Help'))
        util.ocr_verbose(crop=util.expand_locator(t, 200))
        t = u.find_text('Log Files')
        t.move() # A click will close the menu on macOS. Just move the cursor.
        util.take_screenshot()
        util.ocr_verbose(crop=util.expand_locator(t, 450))
        util.click_verbose(u.find_text('Upload Current Log File'))
        util.take_screenshot()
        sleep(4)
        util.take_screenshot()
        pyautogui.hotkey('enter')
        util.take_screenshot()


if __name__ == '__main__':
    unittest.main()
