import sys
from time import sleep
import unittest
import obstest
import obsplugin
import util


class OBSStatsTest(obstest.OBSTest):
    def setUp(self):
        super().setUp(run=False)

    def test_volmeter_vertical(self):
        if sys.platform == 'win32':
            obsplugin.download_install_plugin('norihiro/obs-asynchronous-audio-source')
        self.obs.config.get_global()['BasicWindow']['VerticalVolControl'] = 'true'
        self.obs.config.save_global()

        self.obs.run()

        if sys.platform == 'win32':
            cl = self.obs.get_obsws()
            cl.send('CreateInput', {
                'inputName': 'Sine wave',
                'sceneName': 'Scene',
                'inputKind': 'net.nagater.obs.' + 'asynchronous-audio-source',
                'inputSettings': {
                    'rate': 48000,
                },
            })

        sleep(2)
        util.take_screenshot()


if __name__ == '__main__':
    unittest.main()
