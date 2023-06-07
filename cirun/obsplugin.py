'''
This module provides functions to download and install plugins released on GitHub.
The release format, such as file names and content-types, assumes the one made by norihiro.
'''

import hashlib
import json
import os
import re
import subprocess
import urllib.request
import tempfile
import zipfile


_plugin_cache_dir = 'plugin-cache'

_installed_deb_packages = set()
_installed_windows_files = set()


def _gh_urlopen(url):
    req = urllib.request.Request(url)
    if 'GITHUB_TOKEN' in os.environ:
        GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
        req.add_header('authorization', f'Bearer {GITHUB_TOKEN}')
    return urllib.request.urlopen(req)


def download_plugin(repo_name, file_re):
    '''
    Download latest plugin.
    repo_name - owner/repo on github.com
    file_re - file name filter to download
    return - file name that was downloaded
    '''
    if isinstance(file_re, str):
        file_re = re.compile(file_re)

    with _gh_urlopen(f'https://api.github.com/repos/{repo_name}/releases') as res:
        releases = res.read()
    releases = json.loads(releases.decode())
    latest = releases[0]

    has_obs27 = False
    has_obs28 = False
    aa = []
    for a in latest['assets']:
        name = a['name']
        if file_re.match(name):
            aa.append(a)
            if 'obs27' in name:
                has_obs27 = True
            if 'obs28' in name:
                has_obs28 = True
            print(f'Info: candidate: {name}')

    aa = sorted(aa, key=lambda a: a['name'])
    url = None
    expected_size = 0
    for a in aa:
        name = a['name']
        if has_obs27 and has_obs28 and ('obs27' in name):
            continue
        url = a['browser_download_url']
        expected_size = a['size']

    if not url:
        print('Error: no matching package is found. Available packages are as below.')
        for a in latest['assets']:
            print('  ' + a['name'])
        raise ValueError(f'No matching package for {file_re}')

    try:
        dirname = _plugin_cache_dir + '/' + hashlib.sha1(url.encode()).hexdigest()
        os.makedirs(dirname, mode=0o755, exist_ok=True)
        name = dirname + '/' + name
        with open(name, 'rb') as f:
            if len(f.read()) == expected_size:
                print(f'Info: Using cached file: {name}')
                return name
    except:
        pass

    print(f'Info: Downloading "{name}"...')

    with _gh_urlopen(url) as res:
        with open(name, 'wb') as f:
            f.write(res.read())

    return name


def install_plugin_ubuntu_deb_dpkg(filename):
    '''
    Install a DEB plugin on Ubuntu using 'apt-get' command.
    filename - file name on this system.
    '''
    with subprocess.Popen(['sudo', 'apt-get', 'install', '-y', os.path.abspath(filename)]) as p:
        ret = p.wait()
        if ret != 0:
            raise Exception(f'Failed to install the package {filename} with return code {ret}.')


def install_plugin_windows_zip(filename):
    '''
    Install a ZIP plugin for macOS.
    filename - file name on this system.
    '''
    dirname = 'obs-studio'

    with zipfile.ZipFile(filename) as z:
        z.extractall(dirname)
        for a in z.namelist():
            _installed_windows_files.add(dirname + '/' + a)


def download_install_plugin_ubuntu(repo_name):
    '''
    Download and install the latest plugin.
    repo_name - owner/repo on github.com to download and install.
    Unlike macOS, installed plugin need to be removed by uninstall_all_plugins_ubuntu() or uninstall_all_plugins()
    '''
    filename = download_plugin(repo_name, '.*-ubuntu.*\.deb$')
    install_plugin_ubuntu_deb_dpkg(filename)

    # Assuming the package name is same as the repository name.
    # FIXME: Instead, check the names of the installed packages.
    _installed_deb_packages.add(repo_name.split('/')[-1])


def uninstall_dpkg(pkg):
    with subprocess.Popen(['sudo', 'dpkg', '-r', pkg]) as p:
        ret = p.wait()
        if ret != 0:
            raise Exception(f'Failed to install the package {filename} with return code {ret}.')


def uninstall_all_plugins_ubuntu():
    for pkg in _installed_deb_packages:
        uninstall_dpkg(pkg)
    _installed_deb_packages.clear()


def uninstall_all_plugins_windows():
    rm_dirs = list()
    for f in _installed_windows_files:
        try:
            os.remove(f)
            print(f'removed a file "{f}"')
        except:
            rm_dirs.append(f)
    rm_dirs.sort(reverse=True)
    for f in rm_dirs:
        try:
            os.rmdir(f)
            print(f'removed a directory "{f}"')
        except:
            print(f'could not remove "{f}"')
            pass
    _installed_windows_files.clear()


def install_plugin_macos_zip(filename):
    '''
    Install a ZIP plugin for macOS.
    filename - file name on this system.
    '''
    dirname = os.environ['HOME'] + '/Library/Application Support/obs-studio/plugins/'
    os.makedirs(dirname, exist_ok=True)

    with zipfile.ZipFile(filename) as z:
        z.extractall(dirname)


def install_plugin_macos_pkg(filename):
    '''
    Install a PKG plugin for macOS.
    filename - file name on this system.
    '''
    dirname = os.environ['HOME'] + '/Library/Application Support/obs-studio/plugins/'
    os.makedirs(dirname, exist_ok=True)

    # FIXME: The command 'sudo installer -pkg filename -target $HOME' cannot install to home but root.
    with tempfile.NamedTemporaryFile(suffix='.cpio') as t:
        with subprocess.Popen(['7z', 'x', '-so', filename], stdout=t.file) as p:
            ret = p.wait()
            if ret != 0:
                raise Exception(f'Failed to extract the file {filename} with return code {ret}.')

        t.file.close()

        with subprocess.Popen(['7z', 'x', '-o'+os.environ['HOME'], t.name]) as p:
            ret = p.wait()
            if ret != 0:
                raise Exception(f'Failed to extract the wrapped package in {filename} with return code {ret}.')


def download_install_plugin_macos(repo_name):
    '''
    Download and install the latest plugin.
    repo_name - owner/repo on github.com to download and install.
    '''
    if repo_name == 'glikely/obs-ptz':
        filename = download_plugin(repo_name, '.*-macos-(universal|x86_64).pkg$')
        install_plugin_macos_pkg(filename)
    else:
        # Assumes the package names are the usual norihiro's convention.
        filename = download_plugin(repo_name, '.*-macos(-universal|-x86_64|).zip$')
        install_plugin_macos_zip(filename)


def download_install_plugin_windows(repo_name):
    '''
    Download and install the plugin for Windows.
    repo_name - owner/repo on github.com to download and install.
    '''
    # Assumes the package names are the usual norihiro's convention.
    filename = download_plugin(repo_name, '.*-Windows.zip$')
    install_plugin_windows_zip(filename)


def download_install_plugin(repo_name):
    '''
    Download and install the latest plugin.
    This function will automatically detect the platform.
    repo_name - owner/repo on github.com to download and install.
    '''
    import sys
    if sys.platform == 'darwin':
        return download_install_plugin_macos(repo_name)

    if sys.platform == 'win32':
        return download_install_plugin_windows(repo_name)

    import tiny
    if tiny.is_ubuntu():
        return download_install_plugin_ubuntu(repo_name)

    raise Exception(f'Unsupported platform ({sys.platform}) to install {repo_name}')


def uninstall_all_plugins():
    uninstall_all_plugins_ubuntu()
    uninstall_all_plugins_windows()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
            prog = 'obsplugin',
            description = 'Download a plugin for obs-studio and install it')
    parser.add_argument('repo_name', help='owner/repo on github.com')
    parser.add_argument('--ubuntu', action='store_true', help='Select a package for Ubuntu.')
    parser.add_argument('--macos', action='store_true', help='Select a package for macOS.')
    parser.add_argument('--windows', action='store_true', help='Select a package for Windows.')
    parser.add_argument('--uninstall', action='store_true', help='After installing, uninstall it.')
    args = parser.parse_args()

    if args.ubuntu:
        download_install_plugin_ubuntu(args.repo_name)

    if args.macos:
        download_install_plugin_macos(args.repo_name)

    if args.windows:
        download_install_plugin_windows(args.repo_name)

    if not args.ubuntu and not args.macos and not args.windows:
        download_install_plugin(args.repo_name)

    if args.ubuntu and args.uninstall:
        uninstall_all_plugins_ubuntu()

    if args.windows and args.uninstall:
        uninstall_all_plugins_windows()
