'''
Functions in this module will create sample media files.
'''

import subprocess
import os


_p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-version'])
if _p.wait() != 0:
    raise Exception('cannot run ffmpeg')


default_ext='flv'


def _is_exist(fname):
    try:
        with open(fname):
            return True
    except:
        return False


def lavfi_testsrc2(ext=None):
    if not ext:
        ext = default_ext
    fname = os.path.abspath('lavfi_testsrc2.' + ext)
    if _is_exist(fname):
        return fname

    p = subprocess.Popen([
        'ffmpeg',
        '-loglevel', 'error',
        '-f', 'lavfi', '-i', 'testsrc2=d=15:size=1280x720',
        '-qscale', '0',
        fname])
    p.wait()

    return fname


if __name__ == '__main__':
    import sys
    for a in sys.argv[1:]:
        f = a + '()'
        print(eval(f))
