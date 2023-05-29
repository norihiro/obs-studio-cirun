import sys


def is_ubuntu():
    '''
    Tests the platform is Ubuntu or not.
    If running on Ubuntu, return a version string such as '22.04.1'.
    If not, returns None.
    '''
    if sys.platform != 'linux':
        return None

    try:
        with open('/etc/issue') as f:
            l = f.read()
        l = l.split('\n', 1)[0].split(' ')
        if l[0] == 'Ubuntu':
            return l[1]
    except:
        pass
    return None
