import sys
from time import sleep
import re
import unittest
import obstest
import obsplugin


def _find_line_re(lines, cond):
    if isinstance(cond, str):
        cond = re.compile(cond)

    for l in lines:
        if cond.search(l):
            return True
    return False


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
        self.assertTrue(_find_line_re(loglines, cond))

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


if __name__ == '__main__':
    unittest.main()
