'''
This module provides a functionality to record screen using FFmpeg.
'''

import os
import sys
import subprocess
import pyautogui
from time import sleep


class DesktopRecord:
    def __init__(self, filename='desktop.mkv', framerate=5, start=True):
        self._proc = None
        self.framerate = framerate
        self.filename = filename
        if start:
            self.start()

    def start(self):
        '''Starts screen recording'''

        screen_size = pyautogui.size()

        if sys.platform == 'linux':
            fmt = 'x11grab'
            disp = os.environ['DISPLAY']
        elif sys.platform == 'darwin':
            fmt = 'avfoundation'
            disp = '0' # TODO: ffmpeg -f avfoundation -list_devices true -i ""

        self._proc = subprocess.Popen([
            'ffmpeg',
            '-loglevel', 'error',
            '-video_size', f'{screen_size.width}x{screen_size.height}',
            '-framerate', f'{self.framerate}',
            '-f', fmt,
            '-i', disp,
            '-x264-params', f'keyint={self.framerate*2}:min-keyint={self.framerate}',
            '-y', self.filename,
            ], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def stop(self):
        if not self._proc:
            return

        self._proc.stdin.write('q'.encode())
        self._proc.stdin.flush()

        try:
            self._proc.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            self._proc.send_signal(subprocess.signal.SIGINT)
            self._proc.communicate()


if __name__ == '__main__':
    r = DesktopRecord()
    r.start()
    sleep(5)
    r.stop()

