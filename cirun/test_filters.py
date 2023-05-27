import os
import random
import sys
from time import sleep
import unittest
import pyautogui
import obstest
import util


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
            },
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
            },
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
        },
    })

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
            _create_scene_with_color(cl, scene_name, source_name, int(random.uniform(0xFF000000, 0xFFFFFFFF)))
            cl.send('SetCurrentProgramScene', {'sceneName': scene_name})

            with self.subTest(filterKind=f['filterKind']):
                cl.send('CreateSourceFilter', f)
                cl.send('GetSourceFilter', f)
                ff.append(f)

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
