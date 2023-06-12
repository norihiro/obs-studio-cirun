import os
import random
import sys
import re
from time import sleep
import unittest
import pyautogui
import obstest
import util
import ffmpeg_gen
import obsplugin


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

filters_audio = [
        {
            'sourceName': 'inv',
            'filterName': 'inv',
            'filterKind': 'invert_polarity_filter',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'gain',
            'filterName': 'gain',
            'filterKind': 'gain_filter',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'expander',
            'filterName': 'expander',
            'filterKind': 'expander_filter',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'upward-compressor',
            'filterName': 'upward-compressor',
            'filterKind': 'upward_compressor_filter',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'eq',
            'filterName': 'eq',
            'filterKind': 'basic_eq_filter',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'compressor',
            'filterName': 'compressor',
            'filterKind': 'compressor_filter',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'compressor-sidechain',
            'filterName': 'compressor',
            'filterKind': 'compressor_filter',
            'filterSettings': {
                'sidechain_source': 'compressor',
            },
        },
        {
            'sourceName': 'limiter',
            'filterName': 'limiter',
            'filterKind': 'limiter_filter',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'noise-gate',
            'filterName': 'noise-gate',
            'filterKind': 'noise_gate_filter',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'noise-suppress',
            'filterName': 'noise-suppress',
            'filterKind': 'noise_suppress_filter_v2',
            'filterSettings': {
            },
        },
        {
            'sourceName': 'vst',
            'filterName': 'vst',
            'filterKind': 'vst_filter',
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


def _version_down(scenes):
    v_re = re.compile(r'_v[1-9][0-9]*$')
    ret = []
    for s in scenes['sources']:
        if 'filters' not in s:
            continue
        for f in s['filters']:
            versioned_id = f['versioned_id']
            m = re.search(v_re, versioned_id)
            if not m:
                continue
            version = int(versioned_id[m.start() + 2:]) - 1
            if version > 1:
                versioned_id_new = versioned_id[:m.start()] + f'_v{version}'
            else:
                versioned_id_new = versioned_id[:m.start()]
            print(f'Info: changing {versioned_id} to {versioned_id_new}', flush=True)
            f['versioned_id'] = versioned_id_new
            ret.append({
                'inputName': s['name'],
                'filterName': f['name'],
            })
    if ret:
        scenes.save()
    return ret


class OBSFilterTest(obstest.OBSTest):
    def setUp(self):
        super().setUp(run=False)

    def tearDown(self):
        super().tearDown()
        obsplugin.uninstall_all_plugins()

    def test_add_filters(self):
        self.obs.run()
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

        with self.subTest(msg='open setting dialogs'):
            for f in ff:
                cl.send('SetCurrentProgramScene', {'sceneName': 'Scene ' + f['sourceName']})
                cl.send('OpenInputFiltersDialog', {'inputName': f['sourceName']})
                util.take_screenshot()
                pyautogui.hotkey('esc')

        with self.subTest(msg='exit and start again'):
            self.assertTrue(obstest._is_obs_running())
            self.obs.term()
            self.assertFalse(obstest._is_obs_running())
            self.obs.run()
            self.assertTrue(obstest._is_obs_running())

        self.obs.term()
        self.assertFalse(obstest._is_obs_running())

        version_down = 0
        while True:
            modified = _version_down(self.obs.config.get_scenecollection())
            if not modified:
                break;
            version_down += 1
            with self.subTest(msg=f'version_down {version_down}'):
                self.obs.run()
                self.assertTrue(obstest._is_obs_running())
                cl = self.obs.get_obsws()
                for m in modified:
                    cl.send('SetCurrentProgramScene', {'sceneName': 'Scene ' + f['sourceName']})
                    cl.send('OpenInputFiltersDialog', m)
                    sleep(0.5)
                    pyautogui.hotkey('esc')
                self.obs.term()
                self.assertFalse(obstest._is_obs_running())

    def test_filters_audio(self):
        obsplugin.download_install_plugin('norihiro/obs-asynchronous-audio-source')
        self.obs.run()
        cl = self.obs.get_obsws()

        ff = []
        for f in filters_audio:
            name = f['sourceName']
            with self.subTest(filterKind=f['filterKind']):
                cl.send('CreateInput', {
                    'inputName': name,
                    'sceneName': 'Scene',
                    'inputKind': 'net.nagater.obs.' + 'asynchronous-audio-source',
                    'inputSettings': {
                        'rate': 48000,
                    },
                })
                cl.send('CreateSourceFilter', f)
                ff.append(f)
                # TODO: Check volume

        with self.subTest(msg='open setting dialogs'):
            for f in ff:
                cl.send('OpenInputFiltersDialog', {'inputName': f['sourceName']})
                pyautogui.hotkey('esc')

        with self.subTest(msg='exit and start again'):
            self.assertTrue(obstest._is_obs_running())
            self.obs.term()
            self.assertFalse(obstest._is_obs_running())
            self.obs.run()
            self.assertTrue(obstest._is_obs_running())
            self.obs.term()
            self.assertFalse(obstest._is_obs_running())

        self.assertFalse(obstest._is_obs_running())

        version_down = 0
        while True:
            modified = _version_down(self.obs.config.get_scenecollection())
            if not modified:
                break;
            version_down += 1
            with self.subTest(msg=f'version_down {version_down}'):
                self.obs.run()
                self.assertTrue(obstest._is_obs_running())
                cl = self.obs.get_obsws()
                for m in modified:
                    cl.send('OpenInputFiltersDialog', m)
                    sleep(0.5)
                    pyautogui.hotkey('esc')
                self.obs.term()
                self.assertFalse(obstest._is_obs_running())


if __name__ == '__main__':
    unittest.main()
