import os
import random
import sys
from time import sleep
import unittest
import pyautogui
import obstest
import util

def _create_scene_with_color(cl, scene_name, source_name, color):
    if not source_name:
        source_name = 'color-' + scene_name
    cl.send('CreateScene', {'sceneName': scene_name})
    cl.send('CreateInput', {
        'inputName': source_name,
        'sceneName': scene_name,
        'inputKind': 'color_source_v3',
        'inputSettings': {
            'color': color,
            'width': 640,
            'height': 360,
        },
    })


class OBSProjectorTest(obstest.OBSTest):
    def setUp(self):
        super().setUp(run=False)

    def test_open_projectors(self):
        self.obs.config.get_global()['BasicWindow']['TransitionOnDoubleClick'] = 'true'
        self.obs.config.save_global()

        self.obs.run()

        cl = self.obs.get_obsws()

        cl.set_studio_mode_enabled(True)

        for i in range(0, 16):
            _create_scene_with_color(cl, f'Scene {i}', None, int(random.uniform(0xFF000000, 0xFFFFFFFF)))

        cl.send('SetCurrentPreviewScene', {'sceneName': 'Scene 0'})
        cl.send('SetCurrentProgramScene', {'sceneName': 'Scene 1'})

        with self.subTest(msg='source'):
            cl.send('OpenSourceProjector', {'sourceName': 'Scene 2'})
            util.take_screenshot()
            self._close_projector()

        with self.subTest(msg='program'):
            cl.send('OpenVideoMixProjector', {'videoMixType': 'OBS_WEBSOCKET_VIDEO_MIX_TYPE_PROGRAM'})
            util.take_screenshot()
            self._close_projector()

        with self.subTest(msg='preview'):
            cl.send('OpenVideoMixProjector', {'videoMixType': 'OBS_WEBSOCKET_VIDEO_MIX_TYPE_PREVIEW'})
            util.take_screenshot()
            self._close_projector()

        with self.subTest(msg='multiview'):
            cl.send('OpenVideoMixProjector', {'videoMixType': 'OBS_WEBSOCKET_VIDEO_MIX_TYPE_MULTIVIEW', 'monitorIndex': 0})
            util.take_screenshot()

            for i in range(8):
                self._click_random(method=pyautogui.click)
                util.take_screenshot()
                pyautogui.doubleClick()
                util.take_screenshot()

        with self.subTest(msg='always-on-top'):
            util.take_screenshot()
            pyautogui.rightClick()
            sleep(0.2)
            pyautogui.hotkey('up')
            pyautogui.hotkey('up')
            sleep(1.0)
            pyautogui.hotkey('enter')

        with self.subTest(msg='close'):
            pyautogui.rightClick()
            sleep(0.5)
            pyautogui.hotkey('up')
            sleep(0.5)
            pyautogui.hotkey('enter')
            util.take_screenshot()

    def _close_projector(self):
        if sys.platform == 'darwin':
            sleep(1)
            pyautogui.hotkey('command', 'w')
        else:
            sleep(1)
            pyautogui.rightClick(util.current_window_center())
            sleep(0.5)
            pyautogui.hotkey('up')
            sleep(0.5)
            pyautogui.hotkey('enter')

    def _click_random(self, method):
        cx = int(random.uniform(4, util.u.screenshot.width - 4))
        cy = int(random.uniform(util.u.screenshot.height / 2, util.u.screenshot.height - 4))
        method((cx, cy))

    def test_all_multiview_layouts(self):
        self.obs.config.get_global()['BasicWindow']['TransitionOnDoubleClick'] = 'true'

        with self.subTest(msg=f'multiview-setup'):
            self.obs.run()
            cl = self.obs.get_obsws()
            for i in range(0, 25):
                _create_scene_with_color(cl, f'Scene {i}', None, int(random.uniform(0xFF000000, 0xFFFFFFFF)))
            cl.send('SetStudioModeEnabled', {'studioModeEnabled': True})
            cl.send('RemoveScene', {'sceneName': 'Scene'})
            util.take_screenshot()
            self.obs.term()
            self.assertFalse(obstest._is_obs_running())

        for multiview_layout in range(0, 10):
            with self.subTest(msg=f'multiview-{multiview_layout}'):
                self.assertFalse(obstest._is_obs_running())
                self.obs.config.get_global()['BasicWindow']['MultiviewLayout'] = f'{multiview_layout}'
                self.obs.config.save_global()

                self.obs.run()
                cl = self.obs.get_obsws()
                cl.send('OpenVideoMixProjector', {'videoMixType': 'OBS_WEBSOCKET_VIDEO_MIX_TYPE_MULTIVIEW', 'monitorIndex': 0})

                for i in range(8):
                    self._click_random(method=pyautogui.click)
                    if i == 7:
                        util.take_screenshot()
                    pyautogui.doubleClick()


                self.obs.term()
                self.assertFalse(obstest._is_obs_running())


if __name__ == '__main__':
    unittest.main()
