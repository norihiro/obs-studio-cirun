'''
Functions in this module will create sample media files.
'''

import subprocess
import os


default_ext = 'flv'
cache_path = 'ffmpeg_gen-cache/'


_has_ffmpeg = False
try:
    _p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-version'])
    if _p.wait() == 0:
        _has_ffmpeg = True
except:
    pass


def _is_exist(fname):
    try:
        with open(fname):
            return True
    except:
        return False


def lavfi_testsrc2(ext=None):
    if not ext:
        ext = default_ext
    fname = os.path.abspath(cache_path + 'lavfi_testsrc2.' + ext)
    if _is_exist(fname):
        return fname

    if not _has_ffmpeg:
        return None

    os.makedirs(cache_path, exist_ok=True)

    p = subprocess.Popen([
        'ffmpeg',
        '-loglevel', 'error',
        '-f', 'lavfi', '-i', 'testsrc2=d=15:size=1280x720',
        '-qscale', '0',
        fname])
    p.wait()

    return fname


def lavfi_testsrc_gif():
    fname = os.path.abspath(cache_path + 'lavfi_testsrc.gif')
    if _is_exist(fname):
        return fname

    if not _has_ffmpeg:
        return None

    os.makedirs(cache_path, exist_ok=True)

    p = subprocess.Popen([
        'ffmpeg',
        '-loglevel', 'error',
        '-f', 'lavfi', '-i', 'testsrc=d=6:size=256x192',
        fname])
    p.wait()

    return fname


if __name__ == '__main__':
    import sys
    for a in sys.argv[1:]:
        f = a + '()'
        print(eval(f))
