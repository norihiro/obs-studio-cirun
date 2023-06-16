import json
import os
import random
import sys
import tempfile
from time import sleep
import unittest
import pyautogui
import obstest
import util

def req_batch(cl, requests, executionType=0):
    '''
    cl - obsws_python client, usually created by `self.obs.get_obsws()`
    requests - array of request, each request is a tuple of type and data.
    '''
    requests_data = [{'requestType': t, 'requestData': d} for t, d in requests]
    payload = {
            'op': 8,
            'd': {
                'requestId': str(random.uniform(0, 9999)),
                'executionType': executionType,
                'requests': requests_data,
            },
    }
    ws = cl.base_client.ws
    ws.send(json.dumps(payload))
    json.loads(ws.recv())


def _create_scene_with_color(cl, scene_name, source_name, color):
    global next_executionType
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

        with self.subTest(msg='sources'):
            cl.send('GetSourceActive', {'sourceName': 'color-random'})
            cl.send('GetSourceScreenshot', {'sourceName': 'color-random', 'imageFormat': 'jpeg', 'imageWidth': 160, 'imageHeight': 90})
            with tempfile.TemporaryDirectory() as td:
                cl.send('SaveSourceScreenshot', {'sourceName': 'color-random', 'imageFormat': 'png', 'imageFilePath': str(td) + '/a.png', 'imageWidth': 160, 'imageHeight': 90})
            cl.send('GetSourcePrivateSettings', {'sourceName': 'color-random'})
            cl.send('SetSourcePrivateSettings', {'sourceName': 'color-random', 'sourceSettings': {}})

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

        with self.subTest(msg='general'):
            cl.send('GetVersion')
            cl.send('GetStats')
            cl.send('BroadcastCustomEvent', {'eventData': {'type': 'test_ws'}})
            cl.send('GetHotkeyList')
            cl.send('TriggerHotkeyByName', {'hotkeyName': 'OBSBasic.SplitFile'})
            cl.send('TriggerHotkeyByKeySequence', {'keyId': 'OBS_KEY_A', 'keyModifiers': {'shift': True}})
            cl.send('TriggerHotkeyByKeySequence', {'keyId': 'OBS_KEY_A', 'keyModifiers': {'control': True}})
            cl.send('TriggerHotkeyByKeySequence', {'keyId': 'OBS_KEY_A', 'keyModifiers': {'alt': True}})
            cl.send('TriggerHotkeyByKeySequence', {'keyId': 'OBS_KEY_A', 'keyModifiers': {'command': True}})

        with self.subTest(msg='scenes'):
            cl.send('GetGroupList')
            cl.send('GetCurrentProgramScene')
            cl.send('SetStudioModeEnabled', {'studioModeEnabled': True})
            cl.send('GetCurrentPreviewScene')
            cl.send('SetSceneName', {'sceneName': 'Scene', 'newSceneName': 'New Scene'})
            cl.send('GetSceneItemList', {'sceneName': 'New Scene'})

    def test_batch_types(self):
        cl = self.obs.get_obsws()
        with self.subTest(msg='batch-serialrealtime'):
            req_batch(cl, (
                ('CreateScene', {'sceneName': 'Scene 1'}),
                ('Sleep', {'sleepMillis': 1}),
                ('CreateInput', {
                    'inputName': 'color 1',
                    'sceneName': 'Scene 1',
                    'inputKind': 'color_source_v3',
                    'inputSettings': {
                        'color': int(random.uniform(0xFF000000, 0xFFFFFFFF)),
                        'width': 640,
                        'height': 360,
                    },
                })), executionType=0)

        with self.subTest(msg='batch-serialframe'):
            req_batch(cl, (
                ('CreateScene', {'sceneName': 'Scene 2'}),
                ('Sleep', {'sleepFrames': 1}),
                ('CreateInput', {
                    'inputName': 'color 2',
                    'sceneName': 'Scene 2',
                    'inputKind': 'color_source_v3',
                    'inputSettings': {
                        'color': int(random.uniform(0xFF000000, 0xFFFFFFFF)),
                        'width': 640,
                        'height': 360,
                    },
                })), executionType=1)

        sleep(1)

        with self.subTest(msg='batch-parallel'):
            req_batch(cl, (
                ('RemoveInput', {'inputName': 'Scene 1'}),
                ('RemoveInput', {'inputName': 'color 1'}),
                ), executionType=2)
        sleep(0.1)

    def test_config(self):
        cl = self.obs.get_obsws()

        cl.send('SetPersistentData', {'realm': 'OBS_WEBSOCKET_DATA_REALM_GLOBAL', 'slotName': 'test_ws', 'slotValue': 128})
        v = cl.send('GetPersistentData', {'realm': 'OBS_WEBSOCKET_DATA_REALM_GLOBAL', 'slotName': 'test_ws'}).slot_value
        self.assertEqual(v, 128)

        current_collection = cl.send('GetSceneCollectionList').current_scene_collection_name
        cl.send('CreateSceneCollection', {'sceneCollectionName': 'new collection'})
        cl.send('SetCurrentSceneCollection', {'sceneCollectionName': current_collection})

        current_profile = cl.send('GetProfileList').current_profile_name
        cl.send('CreateProfile', {'profileName': 'new profile'})
        cl.send('GetVideoSettings')
        cl.send('GetStreamServiceSettings')
        cl.send('GetRecordDirectory')
        cl.send('SetCurrentProfile', {'profileName': current_profile})
        cl.send('RemoveProfile', {'profileName': 'new profile'})


if __name__ == '__main__':
    unittest.main()
