import sys
from time import sleep
import unittest
import obstest
import obsplugin


class OBSPluginTest(obstest.OBSTest):
    def setUp(self):
        super().setUp(run=False)

    def test_async_audio_filter(self):
        obsplugin.download_install_plugin_macos('norihiro/obs-async-audio-filter')

        self.obs.run()
        cl = self.obs.get_obsws()

        cl.send('CreateSourceFilter', {
            'sourceName': 'Desktop Audio',
            'filterName': 'async-audio',
            'filterKind': 'net.nagater.obs.' + 'asynchronous-audio-filter'
        })

        sleep(15)

    def test_mute_filter(self):
        obsplugin.download_install_plugin_macos('norihiro/obs-mute-filter')

        self.obs.run()
        cl = self.obs.get_obsws()

        cl.send('CreateSourceFilter', {
            'sourceName': 'Desktop Audio',
            'filterName': 'mute-audio',
            'filterKind': 'net.nagater.obs-mute-filter.' + 'mute-filter'
        })

        sleep(1)


# So far, This test works for macOS.
# TODO: Also implement for Ubuntu 22.04.
if sys.platform != 'darwin':
    del OBSPluginTest


if __name__ == '__main__':
    unittest.main()
