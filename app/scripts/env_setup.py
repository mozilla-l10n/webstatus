#! /usr/bin/env python

import os
import subprocess
import sys


def import_library(libraries_path, type, name, url, version):
    library_path = os.path.join(libraries_path, name)
    if not os.path.isdir(library_path):
        try:
            print('Cloning {0}...'.format(name))
            if type == 'hg':
                commands = ['hg', 'clone', url, library_path]
                if version != '':
                    commands.extend(['-u', version])
                cmd_status = subprocess.check_output(commands,
                                                     stderr=subprocess.STDOUT,
                                                     shell=False)
                print(cmd_status)
            elif type == 'git':
                commands = ['git', 'clone', url, library_path]
                cmd_status = subprocess.check_output(commands,
                                                     stderr=subprocess.STDOUT,
                                                     shell=False)
                print(cmd_status)
                if version != '':
                    commands = ['git', 'checkout', version]
                    cmd_status = subprocess.check_output(commands,
                                                         stderr=subprocess.STDOUT,
                                                         shell=False)
                    print(cmd_status)
        except Exception as e:
            print(e)
    sys.path.insert(0, library_path)


libraries_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir, 'libraries'))

# Import compare-locales
import_library(
    libraries_path, 'hg', 'compare-locales',
    'https://hg.mozilla.org/l10n/compare-locales', 'RELEASE_1_1')
try:
    from compare_locales import parser
except ImportError:
    print('Error importing compare-locales library')
    sys.exit(1)

# Import polib
import_library(
    libraries_path, 'hg', 'polib',
    'https://bitbucket.org/izi/polib', '1.0.7')
try:
    import polib
except ImportError:
    print('Error importing polib library')
    sys.exit(1)
