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
        util.ocr_mainmenu()
        util.take_screenshot(capture=False, draw_cb=util.draw_ocrdata)
        t = util.click_verbose(u.find_text('Tools Help'), location_ratio=(0.8, 0.5))
        util.ocr_verbose(crop=util.expand_locator(t, (-30, -50, 180, 140)))
        try:
            t = u.find_text('Log Files')
            t.move() # A click will close the menu on macOS. Just move the cursor.
        except:
            t = None
            pyautogui.hotkey('down')
            pyautogui.hotkey('down')
            pyautogui.hotkey('down')
            pyautogui.hotkey('down')
            pyautogui.hotkey('right') # Log Files
            pyautogui.hotkey('down')
            pyautogui.hotkey('enter')
        if t:
            util.take_screenshot()
            util.ocr_verbose(crop=util.expand_locator(t, (0, 100, 450,  120)))
            util.click_verbose(u.find_text('Upload Current Log File'))
        util.take_screenshot()
        sleep(4)
        util.take_screenshot()
        pyautogui.hotkey('enter')
        util.take_screenshot()


if __name__ == '__main__':
    unittest.main()
