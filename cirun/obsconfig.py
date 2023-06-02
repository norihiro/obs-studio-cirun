'''
This module provides configuration directory access to test obs-studio.
'''

import sys
import os
import shutil
import string
import random
import configparser


def _get_config_dir():
    if sys.platform == 'linux':
        try:
            return os.environ['XDG_CONFIG_HOME'] + '/obs-studio'
        except KeyError:
            return os.environ['HOME'] + '/.config/obs-studio'
    elif sys.platform == 'darwin':
        return os.environ['HOME'] + '/Library/Application Support/obs-studio'
    elif sys.platform == 'win32':
        return os.environ['AppData'] + '/obs-studio'
    else:
        raise Exception(f'Not supported platform: f{sys.platform}')


def _generate_password():
    cand = string.ascii_lowercase + string.digits + string.ascii_uppercase
    return ''.join([random.choice(cand) for i in range(0, 16)])


class OBSConfig:
    '''
    Base class to access configuration directory for obs-studio.
    '''
    def __init__(self):
        self.path = _get_config_dir()
        self._global = None

    def save(self, name):
        '''
        Save the current state
        name - A path to save the state into. Same name can be passed to OBSConfigCopyFromSaved.
        '''
        shutil.rmtree(name, ignore_errors=True)
        shutil.copytree(self.path + '/', name, symlinks=True)

    def _move_logs(self, path_logs, dest):
        try:
            for f in os.listdir(path_logs):
                try:
                    shutil.move(path_logs + f, dest)
                except FileNotFoundError:
                    break
                except:
                    pass
        except:
            pass

    def move_logs(self):
        dest = './logs/'
        self._move_logs(self.path + '/logs/', dest)
        self._move_logs(self.path + '/crashes/', dest)

    def _clean_config_dir(self):
        self.move_logs()
        shutil.rmtree(self.path, ignore_errors=True)

    def clear_cache(self):
        self._global = None

    def get_global(self):
        if self._global:
            return self._global
        self._global = configparser.RawConfigParser()
        self._global.optionxform = lambda option: option
        self._global.read(self.path + '/global.ini', 'utf-8-sig')
        return self._global

    def save_global(self):
        if not self._global:
            return
        os.makedirs(self.path, mode=0o755, exist_ok=True)
        with open(self.path + '/global.ini', 'w') as f:
            self._global.write(f, space_around_delimiters=False)

    def __getitem__(self, section):
        config = self.get_global()
        try:
            config.add_section(section)
        except configparser.DuplicateSectionError:
            pass
        return config[section]

    def clear_firstrun(self):
        self['General']['FirstRun'] = 'true'

    def enable_websocket(self):
        config_obsws = self['OBSWebSocket']
        config_obsws['FirstLoad'] = 'false'
        config_obsws['ServerEnabled'] = 'true'
        config_obsws['ServerPort'] = '4455'
        config_obsws['AlertsEnabled'] = 'false'
        config_obsws['AuthRequired'] = 'true'
        config_obsws['ServerPassword'] = _generate_password()
        self.save_global()

    def get_profile(self, name=None):
        if not name:
            name = self.get_global()['Basic']['ProfileDir']
        return OBSProfile(self.path + '/basic/profiles/' + name)


class OBSConfigClean(OBSConfig):
    '''
    Provides clean obs-studio configuration.
    '''
    def __init__(self):
        OBSConfig.__init__(self)
        self._clean_config_dir()


class OBSConfigCopyFromSaved(OBSConfig):
    '''
    Restores from a saved configuration and prepare to start obs-studio.
    '''
    def __init__(self, name):
        OBSConfig.__init__(self)
        self._clean_config_dir()
        os.makedirs(os.path.dirname(self.path), mode=0o755, exist_ok=True)
        shutil.copytree(name + '/', self.path, symlinks=True)


class OBSConfigPeekSaved(OBSConfig):
    '''
    Just peeks the saved configuration.
    This might be useful to compare two or more saved config directories.
    '''
    def __init__(self, name):
        self.path = name


def append_preset(config):
    '''
    Adds useful configuration to run obs-studio for testing.
    I don't know this is really useful. It might be better to create a config
    directory by the AutoConfig wizard and then copy that directory.
    '''
    config.clear_firstrun()
    config['Basic']['ConfigOnNewProfile'] = 'false'
    config['General']['ConfirmOnExit'] = 'false'
    config['General']['EnableAutoUpdates'] = 'false'
    config.enable_websocket()
    config.save_global()
    # TODO: Where should I define scene-collection and profile?


class OBSProfile:
    def __init__(self, path=None):
        self.path = path
        self._config = None

    def get_basic(self):
        if self._config:
            return self._config
        self._config = configparser.RawConfigParser()
        self._config.optionxform = lambda option: option
        self._config.read(self.path + '/basic.ini', 'utf-8-sig')
        return self._config

    def __getitem__(self, section):
        config = self.get_basic()
        try:
            config.add_section(section)
        except configparser.DuplicateSectionError:
            pass
        return config[section]

    def save(self):
        config = self.get_basic()
        with open(self.path + '/basic.ini', 'w') as f:
            config.write(f, space_around_delimiters=False)
