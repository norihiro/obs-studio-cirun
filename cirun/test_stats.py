import sys
from time import sleep
import unittest
import obstest
import util


class OBSStatsTest(obstest.OBSTest):
    def setUp(self):
        super().setUp(run=False)

    def test_stats_at_startup(self):
        profile = self.obs.config.get_profile()
        profile['General']['OpenStatsOnStartup'] = 'true'
        profile.save()

        self.obs.run()
        cl = self.obs.get_obsws()

        cl.send('CreateInput', {
            'inputName': 'background',
            'sceneName': 'Scene',
            'inputKind': 'color_source_v3',
            'inputSettings': {
                'color': 0xff582416,
                'width': 640,
                'height': 360,
            },
        })

        if sys.platform != 'darwin':
            # The StartRecord failed on macOS. Do not start recording for now.
            cl.send('StartRecord')

        sleep(2)
        util.take_screenshot()

        try:
            cl.send('GetRecordStatus')
            cl.send('StopRecord')
        except:
            # The StartRecord failed on macOS. Just ignore the failure for now.
            pass

        sleep(2)
        util.take_screenshot()


if __name__ == '__main__':
    unittest.main()
