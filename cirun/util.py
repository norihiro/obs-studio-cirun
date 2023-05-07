import subprocess


def current_window_geometry():
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
