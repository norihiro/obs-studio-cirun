import os
import sys
from time import sleep
import re
import urllib.request
import unittest
import pyautogui
import obstest
import obsplugin
import util
import ffmpeg_gen


def _find_line_re(lines, cond):
    if isinstance(cond, str):
        cond = re.compile(cond)

    for l in lines:
        if cond.search(l):
            return True
    return False


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
            'looping': True,
        },
    })
    return True


def _download_url(url):
    '''
    Download from URL and save on the current directory.
    File name will be taken from the base of the URL.
    url - The URL to download.
    return - Full path of the saved file.
    '''
    req = urllib.request.Request(url)
    res = urllib.request.urlopen(req)
    name = os.getcwd() + '/' + url.rsplit('/', 1)[-1]
    with open(name, 'wb') as f:
        f.write(res.read())
    return name


class OBSPluginTest(obstest.OBSTest):
    def setUp(self):
        super().setUp(run=False)

    def tearDown(self):
        super().tearDown()
        obsplugin.uninstall_all_plugins()

    def _get_loglines(self):
        with open(self.obs.get_logfile()) as f:
            return f.read().split('\n')

    def _assert_log(self, loglines, cond):
        self.assertTrue(_find_line_re(loglines, cond), msg=f'Cannot find "{cond}" in the log file, last log file is {self.obs.get_logfile()}')

    def test_audio_plugins(self):
        obsplugin.download_install_plugin('norihiro/obs-asynchronous-audio-source')
        obsplugin.download_install_plugin('norihiro/obs-async-audio-filter')
        obsplugin.download_install_plugin('norihiro/obs-mute-filter')
        obsplugin.download_install_plugin('norihiro/obs-loudness-dock')

        self.obs.run()
        cl = self.obs.get_obsws()

        with self.subTest(msg='open-loudness-dock'):
            u = util.u
            util.ocr_mainmenu()
            t = util.click_verbose(u.find_text('Docks'))
            util.take_screenshot()
            util.ocr_verbose(crop=util.expand_locator(t, (120, 0, 120, 380)))
            util.click_verbose(u.find_text('Loudness'))
            util.take_screenshot()

        name = 'async-audio'
        cl.send('CreateInput', {
            'inputName': name,
            'sceneName': 'Scene',
            'inputKind': 'net.nagater.obs.' + 'asynchronous-audio-source',
            'inputSettings': {
                'rate': 32000, # also cover libobs resampler
            },
        })

        cl.send('CreateSourceFilter', {
            'sourceName': name,
            'filterName': 'async-audio',
            'filterKind': 'net.nagater.obs.' + 'asynchronous-audio-filter'
        })
        sleep(15)
        util.take_screenshot()

        cl.send('CreateSourceFilter', {
            'sourceName': name,
            'filterName': 'mute-audio',
            'filterKind': 'net.nagater.obs-mute-filter.' + 'mute-filter'
        })
        sleep(1)
        util.take_screenshot()

        self.obs.term()
        log = self._get_loglines()
        self._assert_log(log, '\[obs-async-audio-filter\].*plugin loaded')
        self._assert_log(log, '\[obs-mute-filter\].*plugin loaded')
        self._assert_log(log, '\[obs-asynchronous-audio-source\].*plugin loaded')
        self._assert_log(log, 'Number of memory leaks: 0$')

    def test_color_monitor(self):
        obsplugin.download_install_plugin('norihiro/obs-color-monitor')

        self.obs.run()
        cl = self.obs.get_obsws()

        u = util.u
        util.take_screenshot()
        util.ocr_mainmenu()
        t = util.click_verbose(u.find_text('Tools'))
        util.ocr_verbose(crop=util.expand_locator(t, 270))
        try:
            util.click_verbose(u.find_text('New Scope Dock...'))
        except:
            # If not found, click the last item, assuming there are no other plugins.
            pyautogui.hotkey('up')
            pyautogui.hotkey('enter')
        util.take_screenshot()
        t = u.find_text('Other sources can be selected from the property after creating the dock.')
        util.ocr_verbose(crop=util.expand_locator(t, 70))
        if sys.platform == 'darwin':
            try:
                util.click_verbose(u.find_text('Cancel OK'), location_ratio=(1.0, 0.5))
            except:
                # if not found
                util.click_verbose(u.find_text('Other sources can be selected from the property after creating the dock.'))
                pyautogui.hotkey('enter')
        else:
            util.click_verbose(u.find_text('OK Cancel'), location_ratio=(0.0, 0.5))

        if not _create_scene_with_media(cl, 'Scene 1', 'media-source'):
            _create_scene_with_color(cl, 'Scene 1', 'color source', int(random.uniform(0xFF000000, 0xFFFFFFFF)))
        cl.send('SetCurrentProgramScene', {'sceneName': 'Scene 1'})

        sleep(5)
        util.take_screenshot()

        with self.subTest(msg='exit'):
            self.obs.term()
            log = self._get_loglines()
            self._assert_log(log, 'Number of memory leaks: 0$')
            self.assertFalse(obstest._is_obs_running())

        with self.subTest(msg='run again'):
            self.obs.run()
            sleep(5)
            self.assertTrue(obstest._is_obs_running())
            util.take_screenshot()
            self.obs.term()
            log = self._get_loglines()
            self._assert_log(log, 'Number of memory leaks: 0$')
            self.assertFalse(obstest._is_obs_running())

    def test_face_tracker(self):
        obsplugin.download_install_plugin('norihiro/obs-face-tracker')

        self.obs.run()
        cl = self.obs.get_obsws()

        # A face image to test obs-face-tracker.
        image_url = 'http://spr.nagater.net/~obs-cirun/data/img-0063-crop.jpeg'
        src_name = 'image'
        cl.send('CreateInput', {
            'inputName': src_name,
            'sceneName': 'Scene',
            'inputKind': 'image_source',
            'inputSettings': {
                'file': _download_url(image_url),
            },
        })

        cl.send('CreateSourceFilter', {
            'sourceName': src_name,
            'filterName': 'face_tracker_filter',
            'filterKind': 'face_tracker_filter',
            'filterSettings': {
                "debug_always_show": True,
                "debug_faces": True,
                "debug_notrack": True,
            },
        })

        sleep(5)
        util.take_screenshot()
        sleep(5)
        util.take_screenshot()
        cl.send('OpenInputFiltersDialog', {'inputName': src_name})
        sleep(1)
        util.take_screenshot()
        pyautogui.hotkey('esc')

    def test_vnc(self):
        obsplugin.download_install_plugin('norihiro/obs-vnc')

        self.obs.run()
        cl = self.obs.get_obsws()

        cl.send('CreateInput', {
            'inputName': 'vnc',
            'sceneName': 'Scene',
            'inputKind': 'obs_vnc_source',
            'inputSettings': {
                'host_name': 'localhost',
                'host_port': 5901,
                'plain_passwd': 'password',
            },
        })

    def test_shutdown(self):
        obsplugin.download_install_plugin('norihiro/obs-shutdown-plugin')

        self.obs.run()
        cl = self.obs.get_obsws()

        cl.send('CallVendorRequest', {
            'vendorName': 'obs-shutdown-plugin',
            'requestType': 'shutdown',
            'requestData': {
                'reason': f'requested by {sys.argv[0]}',
                'support_url': 'https://github.com/norihiro/obs-studio-cirun/issues',
                'force': True,
            },
        })

        cl.base_client.ws.close()
        self.obs._obsws = None
        self.assertTrue(self.obs._is_terminated(timeout=10), msg='OBS did not terminated by the plugin.')


if __name__ == '__main__':
    unittest.main()
