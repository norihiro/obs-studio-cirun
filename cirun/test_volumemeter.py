from time import sleep
import unittest
import obstest
import util


class OBSStatsTest(obstest.OBSTest):
    def setUp(self):
        super().setUp(run=False)

    def test_volmete_vertial(self):
        util.set_screenshot_prefix('screenshot/test_volmete_vertial-')

        self.obs.config.get_global()['BasicWindow']['VerticalVolControl'] = 'true'
        self.obs.config.save_global()

        self.obs.run()

        sleep(2)
        util.take_screenshot()


if __name__ == '__main__':
    unittest.main()
