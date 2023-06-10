import json
import os
import random
import sys
from time import sleep
import unittest
import pyautogui
import obstest
import util

def req_batch(cl, requests):
    '''
    cl - obsws_python client, usually created by `self.obs.get_obsws()`
    requests - array of request, each request is a tuple of type and data.
    '''
    requests_data = [{'requestType': t, 'requestData': d} for t, d in requests]
    payload = {
            'op': 8,
            'd': {
                'requestId': str(random.uniform(0, 9999)),
                'executionType': 0,
                'requests': requests_data,
            },
    }
    ws = cl.base_client.ws
    ws.send(json.dumps(payload))
    json.loads(ws.recv())


def _create_scene_with_color(cl, scene_name, source_name, color):
    if not source_name:
        source_name = 'color-' + scene_name
    req_batch(cl, (
        ('CreateScene', {'sceneName': scene_name}),
        ('CreateInput', {
            'inputName': source_name,
            'sceneName': scene_name,
            'inputKind': 'color_source_v3',
            'inputSettings': {
                'color': color,
                'width': 640,
                'height': 360,
            },
        })
    ))


class OBSWSTest(obstest.OBSTest):
    def test_obsws(self):
        cl = self.obs.get_obsws()

        with self.subTest(msg='batch request'):
            _create_scene_with_color(cl, 'Scene Color', 'color-random',
                                     int(random.uniform(0xFF000000, 0xFFFFFFFF)))

        with self.subTest(msg='GetInputKindList'):
            cl.send('GetInputKindList')
            cl.send('GetInputKindList', {'unversioned': True})

        with self.subTest(msg='GetSpecialInputs'):
            cl.send('GetSpecialInputs')

        with self.subTest(msg='RemoveInput'):
            _create_scene_with_color(cl, 'Scene Remove', 'color-remove',
                                     int(random.uniform(0xFF000000, 0xFFFFFFFF)))
            cl.send('RemoveInput', {'inputName': 'color-remove'})

        with self.subTest(msg='SetInputName'):
            _create_scene_with_color(cl, 'Scene Rename', 'color-rename',
                                     int(random.uniform(0xFF000000, 0xFFFFFFFF)))
            cl.send('SetInputName', {'inputName': 'color-rename', 'newInputName': 'color-renamed'})

        with self.subTest(msg='GetInputDefaultSettings'):
            cl.send('GetInputDefaultSettings', {'inputKind': 'color_source_v3'})

        with self.subTest(msg='GetInputSettings'):
            cl.send('GetInputSettings', {'inputName': 'color-random'})

        with self.subTest(msg='UI'):
            r = cl.send('GetStudioModeEnabled')
            self.assertFalse(r.studio_mode_enabled)

            cl.send('SetStudioModeEnabled', {'studioModeEnabled': True})
            r = cl.send('GetStudioModeEnabled')
            self.assertTrue(r.studio_mode_enabled)

            cl.send('SetStudioModeEnabled', {'studioModeEnabled': False})
            r = cl.send('GetStudioModeEnabled')
            self.assertFalse(r.studio_mode_enabled)

            cl.send('GetMonitorList')


if __name__ == '__main__':
    unittest.main()
