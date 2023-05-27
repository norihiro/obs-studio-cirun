import os
import random
import sys
from time import sleep
import unittest
import pyautogui
import obstest
import util
import ffmpeg_gen


filters = [
        {
            'sourceName': 'chroma key',
            'filterName': 'chroma',
            'filterKind': 'chroma_key_filter_v2',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'color key',
            'filterName': 'color',
            'filterKind': 'color_key_filter_v2',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'luma key',
            'filterName': 'luma',
            'filterKind': 'luma_key_filter_v2',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'mask',
            'filterName': 'mask',
            'filterKind': 'mask_filter_v2',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'sharpness',
            'filterName': 'sharpness',
            'filterKind': 'sharpness_filter_v2',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'color correction',
            'filterName': 'color correction',
            'filterKind': 'color_filter_v2',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'color grade',
            'filterName': 'color grade',
            'filterKind': 'clut_filter',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'crop',
            'filterName': 'crop',
            'filterKind': 'crop_filter',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'gpu delay',
            'filterName': 'dly',
            'filterKind': 'gpu_delay',
            'filterSettings': {
                'delay_ms': 200
            },
            'filterSettings1': {
                'delay_ms': 400
            },
            'filterSettings2': {
                'delay_ms': 50
            },
            'sleep_after_creation': 2,
            'sleep_after_update': 2,
        },
        {
            'sourceName': 'async delay',
            'filterName': 'async-dly',
            'filterKind': 'async_delay_filter',
            'filterSettings': {
                'delay_ms': 400
            },
            'type': 'ASYNC_VIDEO',
        },
        {
            'sourceName': 'scale',
            'filterName': 'scale',
            'filterKind': 'scale_filter',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'scroll',
            'filterName': 'scroll',
            'filterKind': 'scroll_filter',
            'filterSettings': {
                'speed_x': 500,
                'speed_y': 500
            },
            'filterSettings1': {
                'loop': False
            },
            'sleep_after_creation': 4,
            'sleep_after_update': 4,
        },
]


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

def _create_scene_with_media(cl, scene_name, source_name):
    fname = ffmpeg_gen.lavfi_testsrc2()
    if not fname:
        return None
    if not source_name:
        source_name = 'media-' + scene_name
    cl.send('CreateScene', {'sceneName': scene_name})
    cl.send('CreateInput', {
        'inputName': source_name,
        'sceneName': scene_name,
        'inputKind': 'ffmpeg_source',
        'inputSettings': {
            'local_file': ffmpeg_gen.lavfi_testsrc2(),
        },
    })
    return True

class OBSFilterTest(obstest.OBSTest):
    def test_add_filters(self):
        util.set_screenshot_prefix('screenshot/test_add_filters-')
        cl = self.obs.get_obsws()

        ff = []

        for f in filters:
            if 'skip' in f and f['skip']:
                continue
            source_name = f['sourceName']
            scene_name = 'Scene ' + source_name

            with self.subTest(filterKind=f['filterKind']):
                if 'type' in f and f['type'] == 'ASYNC_VIDEO':
                    if not _create_scene_with_media(cl, scene_name, source_name):
                        self.skipTest('An async video source is unavailable.')
                else:
                    _create_scene_with_color(cl, scene_name, source_name, int(random.uniform(0xFF000000, 0xFFFFFFFF)))
                cl.send('SetCurrentProgramScene', {'sceneName': scene_name})

                cl.send('CreateSourceFilter', f)
                if 'sleep_after_creation' in f:
                    sleep(f['sleep_after_creation'])
                cl.send('GetSourceFilter', f)
                ff.append(f)

                i = 1
                while f'filterSettings{i}' in f:
                    d = dict(f)
                    d['filterSettings'] = f[f'filterSettings{i}']
                    cl.send('SetSourceFilterSettings', d)
                    if 'sleep_after_update' in f:
                        sleep(f['sleep_after_update'])
                    i += 1

            util.take_screenshot()

        with self.subTest(msg='open setting dialogs'):
            for f in ff:
                cl.send('OpenInputFiltersDialog', {'inputName': f['sourceName']})
                util.take_screenshot()
                pyautogui.hotkey('esc')

        with self.subTest(msg='exit and start again'):
            cl.base_client.ws.close()
            self.assertTrue(obstest._is_obs_running())
            self.obs.term()
            self.assertFalse(obstest._is_obs_running())
            self.obs.run()
            self.assertTrue(obstest._is_obs_running())


if __name__ == '__main__':
    unittest.main()
