import os
import random
import sys
from time import sleep
import unittest
import pyautogui
import obstest
import util


sources = [
        {
            'inputName': 'background',
            'sceneName': 'Background Scene',
            'inputKind': 'color_source_v3',
            'inputSettings': {
                'color': 0xff582416,
                },
            },
        {
            'inputName': 'text',
            'sceneName': 'Scene Text',
            'inputKind': 'text_ft2_source_v2',
            'inputSettings': {
                'text': 'Text Source',
                },
            'update_settings': [
                {
                    'outline': True,
                    },
                {
                    'outline': False,
                    'drop_shadow': True,
                    },
                {
                    'drop_shadow': False,
                    },
                ]
            },
        {
            'inputName': 'images',
            'sceneName': 'Scene Images',
            'inputKind': 'slideshow',
            'inputSettings': {
                'files': [
                    {
                        'value': os.getcwd() + '/screenshot',
                        'selected': False,
                        'hidden': False,
                        },
                    ],
                },
            },
        {
            'inputName': 'browser',
            'sceneName': 'Scene Browser',
            'inputKind': 'browser_source',
            'inputSettings': {
                'url': 'https://www.youtube.com/watch?v=ghuB0ozPttI&list=UULFp_UXGmCCIRaX5pyFljICoQ',
                'reroute_audio': False,
                },
            'sleep_after_creation': 5,
            'update_settings': [
                {
                    'reroute_audio': True
                    },
                {
                    'reroute_audio': False
                    },
                ]
            },
        {
            'inputName': 'xshm',
            'sceneName': 'Scene Desktop',
            'inputKind': 'xshm_input',
            'inputSettings': {
                },
            'skip': (sys.platform != 'linux')
            },
        {
            'inputName': 'screen',
            'sceneName': 'Screen Capture',
            'inputKind': 'screen_capture',
            'inputSettings': {
                },
            'skip': (sys.platform != 'darwin')
            },
        {
            'inputName': 'display',
            'sceneName': 'Display Capture',
            'inputKind': 'display_capture',
            'inputSettings': {
                },
            'skip': (sys.platform != 'darwin')
            },
        ]

background_source = sources[0]['sceneName']


class OBSSourceTest(obstest.OBSTest):
    def test_add_remove_sources(self):
        util.set_screenshot_prefix('screenshot/test_add_remove_sources-')
        cl = self.obs.get_obsws()
        cl.set_studio_mode_enabled(True)
        input_kinds = cl.send('GetInputKindList').input_kinds

        scenes = set()
        for scene in cl.send('GetSceneList').scenes:
            scenes.add(scene['sceneName'])

        for source in sources:
            if 'skip' in source and source['skip']:
                continue
            with self.subTest(inputKind=source['inputKind']):
                sceneName = source['sceneName']
                if not sceneName in scenes:
                    cl.send('CreateScene', {'sceneName': sceneName})
                    scenes.add(sceneName)
                if sceneName != background_source:
                    cl.send('CreateSceneItem', {'sceneName': sceneName, 'sourceName': background_source})
                cl.send('CreateInput', source)
                cl.send('SetCurrentPreviewScene', {'sceneName': sceneName})
                cl.send('SetCurrentProgramScene', {'sceneName': sceneName})
                if 'sleep_after_creation' in source:
                    sleep(source['sleep_after_creation'])
                util.take_screenshot()
                if 'update_settings' in source:
                    for settings in source['update_settings']:
                        name = source['inputName']
                        data = {'inputName': name, 'inputSettings': settings}
                        print('SetInputSettings %s' % data)
                        cl.send('SetInputSettings', data)
                        if 'sleep_after_creation' in source:
                            sleep(source['sleep_after_creation'])
                        util.take_screenshot()

        with self.subTest(msg='exit and start again'):
            self.assertTrue(obstest._is_obs_running())
            self.obs.term()
            self.assertFalse(obstest._is_obs_running())
            self.obs.run()
            self.assertTrue(obstest._is_obs_running())

        with self.subTest(msg='cleanup'):
            cl = self.obs.get_obsws()
            for source in sources:
                sceneName = source['sceneName']
                if sceneName in scenes:
                    cl.send('RemoveScene', {'sceneName': sceneName})
                    scenes.remove(sceneName)
            util.take_screenshot()


if __name__ == '__main__':
    unittest.main()