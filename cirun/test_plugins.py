import sys
from time import sleep
import re
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

        self.obs.run()
        cl = self.obs.get_obsws()

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

        cl.send('CreateSourceFilter', {
            'sourceName': name,
            'filterName': 'mute-audio',
            'filterKind': 'net.nagater.obs-mute-filter.' + 'mute-filter'
        })
        sleep(1)

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

        _create_scene_with_media(cl, 'Scene 1', 'media-source')
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


if __name__ == '__main__':
    unittest.main()
