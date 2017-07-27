#! /usr/bin/env python

import os
import shutil
import subprocess
import sys


def import_library(libraries_path, type, name, url, version):
    library_path = os.path.join(libraries_path, name)

    if os.path.isdir(library_path) and not os.path.isdir(os.path.join(library_path, '.{0}'.format(type))):
        print('Folder {0} is not the expected type of repository. Removing...'.format(
            library_path))
        shutil.rmtree(library_path)

    if not os.path.isdir(library_path):
        try:
            print('Cloning {0}...'.format(name))
            if type == 'hg':
                commands = [
                    'hg', 'clone', url, library_path,
                    '-u', 'default' if version == '' else version]
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
                    commands = ['git', '-C', library_path, 'checkout', version]
                    cmd_status = subprocess.check_output(commands,
                                                         stderr=subprocess.STDOUT,
                                                         shell=False)
                    print(cmd_status)
        except Exception as e:
            print(e)
    sys.path.insert(0, library_path)


libraries_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir, 'libraries'))

# Import Fluent Python library
import_library(
    libraries_path, 'git', 'python-fluent',
    'https://github.com/projectfluent/python-fluent', '0.4.1')
try:
    import fluent.syntax
except ImportError:
    print('Error importing python-fluent library')
    sys.exit(1)

# Import compare-locales
import_library(
    libraries_path, 'hg', 'compare-locales',
    'https://hg.mozilla.org/l10n/compare-locales', 'RELEASE_2_0')
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
