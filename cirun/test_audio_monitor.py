import sys
from time import sleep
import unittest
import obstest
import util

class OBSMonitorTest(obstest.OBSTest):
    def setUp(self):
        super().setUp(run=False)

    def _loop_source_devices(self, cl, device_ids):
        for t in ['OBS_MONITORING_TYPE_MONITOR_ONLY', 'OBS_MONITORING_TYPE_MONITOR_AND_OUTPUT']:
            for d in device_ids:
                print('Info: Setting source device to %s' % d['itemValue'], flush=True)
                cl.send('SetInputSettings', {'inputName': 'Desktop Audio', 'inputSettings': {'device_id': d['itemValue']}})
                cl.send('SetInputAudioMonitorType', {'inputName': 'Desktop Audio', 'monitorType': t})
                sleep(0.1)
                res = cl.send('GetInputAudioMonitorType', {'inputName': 'Desktop Audio'})
                self.assertEqual(res.monitor_type, t)

    @unittest.skipIf(sys.platform == 'win32', 'No desktop audio')
    def test_monitor_types(self):
        self.obs.run()
        cl = self.obs.get_obsws()

        res = cl.send('GetInputPropertiesListPropertyItems', {'inputName': 'Desktop Audio', 'propertyName': 'device_id'})
        device_ids = res.property_items

        self._loop_source_devices(cl, device_ids)

        for mon_dev in device_ids:
            name = mon_dev['itemValue']
            if name == 'default':
                continue

            self.obs.term()
            profile = self.obs.config.get_profile()
            if name[-8:] == '.monitor':
                name = name[:-8]
            print('Info: Setting monitoring device to %s' % name, flush=True)
            profile['Audio']['MonitoringDeviceId'] = name
            profile['Audio']['MonitoringDeviceName'] = mon_dev['itemName']
            profile.save()
            self.obs.run()
            cl = self.obs.get_obsws()

            self._loop_source_devices(cl, device_ids)



if __name__ == '__main__':
    unittest.main()
