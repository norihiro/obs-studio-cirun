from time import sleep
import unittest
import obstest
import util


class OBSStatsTest(obstest.OBSTest):
    def setUp(self):
        super().setUp(run=False)

    def test_volmeter_vertical(self):
        self.obs.config.get_global()['BasicWindow']['VerticalVolControl'] = 'true'
        self.obs.config.save_global()

        self.obs.run()

        sleep(2)
        util.take_screenshot()


if __name__ == '__main__':
    unittest.main()
