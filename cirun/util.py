import os
import subprocess
import sys
from time import sleep
import pyautogui
from untriseptium import Untriseptium
import untriseptium.util


sleep_after_click = 0.2

def current_window_geometry():
    if sys.platform == 'darwin' or sys.platform == 'win32':
        import pygetwindow as gw
        a = gw.getActiveWindow()
        x0 = a.left
        y0 = a.top
        x1 = a.width
        y1 = a.height
    elif sys.platform == 'linux':
        s = subprocess.run(['xdotool', 'getwindowfocus', 'getwindowgeometry'], capture_output=True)
        for line in s.stdout.decode().split('\n'):
            line = line.strip().split(' ')
            if len(line) >= 2 and line[0] == 'Position:':
                x0, y0 = line[1].split(',')
            elif len(line) >= 2 and line[0] == 'Geometry:':
                x1, y1 = line[1].split('x')

    x0 = int(x0)
    y0 = int(y0)
    y1 = int(y1)
    x1 = int(x1)
    return (x0, y0, x0+x1, y0+y1)


def current_window_center():
    loc = current_window_geometry()
    return (int((loc[0] + loc[2]) / 2), int((loc[1] + loc[3]) / 2))


def expand_locator(loc, length):
    '''
    Returns a rectangle expanded by length from the loc.
    The return type is a 4-element tuple.
    loc - 4-element tuple describing a rectangle. Some other types are also accepted.
    '''
    if isinstance(loc, untriseptium.util.TextLocator):
        loc = loc.location
    if isinstance(loc, untriseptium.util.Location):
        loc = (loc.x0, loc.y0, loc.x1, loc.y1)
    if len(loc) == 2:
        loc = (loc[0], loc[1], loc[0], loc[1])

    return (max(0, loc[0] - length), max(0, loc[1] - length), loc[2] + length, loc[3] + length)


def wait_text(text, confidence_threshold=0.9, sleep_each=1, timeout=None, ocrfunc=None):
    '''
    Waits until the specified text appears on the screen.
    text - Expected text that will apear on the screen.
    '''
    time_passed = 0
    while True:
        sleep(sleep_each)
        time_passed += sleep_each
        u.capture()
        if ocrfunc:
            ocrfunc(u)
        tt = u.find_texts(text)
        if len(tt) > 0 and tt[0].confidence > confidence_threshold:
            return tt[0]
        if timeout and time_passed >= timeout:
            s_bestmatch = f'current best match is "{tt[0].text}"' if len(tt) else 'no matching text'
            raise TimeoutError(f'Cannot find "{text}" {s_bestmatch}')


def click_verbose(t, location_ratio=None):
    print(f'Clicking text="{t.text}" location={t.location} confidence={t.confidence}')
    sys.stdout.flush()
    if location_ratio:
        x = int(t.location.x0 * (1.0 - location_ratio[0]) + t.location.x1 * location_ratio[0])
        y = int(t.location.y0 * (1.0 - location_ratio[1]) + t.location.y1 * location_ratio[1])
        u.click((x, y))
        pass
    else:
        t.click()
    global sleep_after_click
    sleep(sleep_after_click)
    return t


def ocr_verbose(**kwargs):
    u.ocr(**kwargs)

    def draw(d):
        if 'crop' in kwargs:
            d.rectangle(kwargs['crop'], outline=(255, 0, 0, 128))
        for t in u.ocrdata:
            if not t.text:
                continue
            try:
                d.text((t.location.x0, t.location.y0), t.text, fill=(255, 0, 0, 128))
            except:
                pass

    take_screenshot(capture=False, draw_cb=draw)


def ocr_topwindow(mode=None, length=0, ratio=-1):
    sleep(0.1)
    u.capture()
    geometry = current_window_geometry()
    if ratio > 0 and (mode=='left' or mode=='right'):
        length = int((geometry[2] - geometry[0]) * ratio)
    elif ratio > 0 and (mode=='top' or mode=='bottom'):
        length = int((geometry[3] - geometry[1]) * ratio)
    if mode=='left':
        geometry = (geometry[0], geometry[1], min(geometry[0] + length, geometry[2]), geometry[3])
    elif mode=='top':
        geometry = (geometry[0], geometry[1], geometry[2], min(geometry[1] + length, geometry[3]))
    elif mode=='right':
        geometry = (min(geometry[2] - length, geometry[0]), geometry[1], geometry[2], geometry[3])
    elif mode=='bottom':
        geometry = (geometry[0], min(geometry[3] - length, geometry[1]), geometry[2], geometry[3])
    u.ocr(crop=geometry)


def ocr_screen(mode=None, length=0, ratio=-1):
    sleep(0.1)
    u.capture()
    screen_size = pyautogui.size()
    if ratio > 0 and (mode=='left' or mode=='right'):
        length = int(screen_size[0] * ratio)
    elif ratio > 0 and (mode=='top' or mode=='bottom'):
        length = int(screen_size[1] * ratio)
    if mode=='left':
        geometry = (0, 0, min(0 + length, screen_size[0]), screen_size[1])
    elif mode=='top':
        geometry = (0, 0, screen_size[0], min(length, screen_size[1]))
    elif mode=='right':
        geometry = (min(screen_size[0] - length, 0), 0, screen_size[0], screen_size[1])
    elif mode=='bottom':
        geometry = (0, min(screen_size[1] - length, 0), screen_size[0], screen_size[1])
    u.ocr(crop=geometry)


_screenshot_prefix = 'screenshot/screenshot-'
_screenshot_index = 0
u = Untriseptium()


def set_screenshot_prefix(name):
    global _screenshot_prefix
    global _screenshot_index
    _screenshot_prefix = name
    _screenshot_index = 0
    os.makedirs(os.path.dirname(name), exist_ok=True)


def take_screenshot(capture=True, draw_cb=None):
    global _screenshot_prefix
    global _screenshot_index
    if capture or not u.screenshot:
        sleep(1)
        u.capture()
        macos_check_fault(capture=False)
    name = f'{_screenshot_prefix}{_screenshot_index:02d}.png'
    print(f'Info: Saving screenshot to {name}')
    sys.stdout.flush()
    u.screenshot.save(name)
    if draw_cb:
        from PIL import ImageDraw
        im = u.screenshot.copy()
        d = ImageDraw.Draw(im)
        draw_cb(d)
        name = f'{_screenshot_prefix}{_screenshot_index:02d}.d.png'
        im.save(name)
    _screenshot_index += 1


def _macos_check_fault_report():
    click_verbose(u.find_text('Report...'))
    sleep(3)

    # Expect to have buttons `Show Details`, `Don't Send`, `Send to Apple`
    u.capture()
    take_screenshot(capture=False)
    cx = u.screenshot.width / 2
    u.ocr(crop=(cx-256, 0, cx+256, u.screenshot.height))
    click_verbose(u.find_text('Show Details'))
    sleep(3)

    # TODO: Navigate further
    u.capture()


def macos_check_fault(capture=True):
    if sys.platform != 'darwin':
        return

    if capture or not u.screenshot:
        u.capture()

    backup = u.ocrdata
    cx = u.screenshot.width / 2
    u.ocr(crop=(cx-128, 0, cx+128, u.screenshot.height))
    tt = u.find_texts('OBS Studio quit unexpectedly.')
    if len(tt) == 0 or tt[0].confidence < 0.9:
        u.ocrdata = backup
        return

    _macos_check_fault_report()
    raise Exception(tt[0].text)


def ocr_mainmenu(capture=True):
    if capture:
        u.capture()

    retry = 5
    while retry > 0:
        retry -= 1
        if sys.platform != 'darwin':
            geo = current_window_geometry()
            u.ocr(crop=(geo[0], geo[1], geo[2], geo[1]+50))

        else:
            u.ocr(crop=(0, 0, u.screenshot.width, 40))

        tt = u.find_texts('File Edit View Docks Profile Scene Collection Tools Help')
        if len(tt) > 0 and tt[0].confidence > 0.8:
            return

        sleep(2)
