import os
import random
import re
import sys
from time import sleep
import unittest
import pyautogui
import obstest
import obsplugin


class OBSAudioBufferingTest(obstest.OBSTest):
    def setUp(self):
        super().setUp(run=False)

    def tearDown(self):
        super().tearDown()
        obsplugin.uninstall_all_plugins()

    def test_audio_fixed_buffering(self):
        obsplugin.download_install_plugin('norihiro/obs-asynchronous-audio-source')
        self.obs.config['Audio']['LowLatencyAudioBuffering'] = 'true'
        self.obs.config.save_global()

        self.obs.run()
        cl = self.obs.get_obsws()
        cl.send('CreateInput', {
            'inputName': 'test-audio-slow',
            'sceneName': 'Scene',
            'inputKind': 'net.nagater.obs.' + 'asynchronous-audio-source',
            'inputSettings': {
                'rate': 48000,
                'skew': -100e+3,
            },
        })
        cl.send('CreateInput', {
            'inputName': 'test-audio-fast',
            'sceneName': 'Scene',
            'inputKind': 'net.nagater.obs.' + 'asynchronous-audio-source',
            'inputSettings': {
                'rate': 48000,
                'skew': +100e+3,
            },
        })
        sleep(6)
        cl.send('SetInputAudioSyncOffset', {
            'inputName': 'test-audio-fast',
            'inputAudioSyncOffset': -200
        })
        cl.send('SetInputAudioSyncOffset', {
            'inputName': 'test-audio-slow',
            'inputAudioSyncOffset': -200
        })
        sleep(2)
        self.obs.term()

    def test_audio_variable_buffering(self):
        obsplugin.download_install_plugin('norihiro/obs-asynchronous-audio-source')
        self.obs.config['Audio']['LowLatencyAudioBuffering'] = 'false'
        self.obs.config.save_global()

        self.obs.run()
        cl = self.obs.get_obsws()
        cl.send('CreateInput', {
            'inputName': 'test-audio',
            'sceneName': 'Scene',
            'inputKind': 'net.nagater.obs.' + 'asynchronous-audio-source',
            'inputSettings': {
                'rate': 48000,
            },
        })

        for i in range(0, 4):
            cl.send('SetInputAudioSyncOffset', {
                'inputName': 'test-audio',
                'inputAudioSyncOffset': -30 * i
            })
            sleep(0.5)

    def test_audio_max_buffering(self):
        obsplugin.download_install_plugin('norihiro/obs-asynchronous-audio-source')
        self.obs.config['Audio']['LowLatencyAudioBuffering'] = 'false'
        self.obs.config.save_global()

        self.obs.run()
        cl = self.obs.get_obsws()
        cl.send('CreateInput', {
            'inputName': 'test-audio',
            'sceneName': 'Scene',
            'inputKind': 'net.nagater.obs.' + 'asynchronous-audio-source',
            'inputSettings': {
                'rate': 48000,
                'skew': -50e+3,
            },
        })

        cl.send('SetInputAudioSyncOffset', {
            'inputName': 'test-audio',
            'inputAudioSyncOffset': -950
        })

        sleep(5)


if __name__ == '__main__':
    unittest.main()
