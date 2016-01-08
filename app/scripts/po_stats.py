#! /usr/bin/env python

import argparse
import glob
import json
import os
import subprocess
import sys

# Import local libraries
library_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir, 'libraries'))

# Polib library (https://bitbucket.org/izi/polib)
polib_path = os.path.join(library_path, 'polib')
if not os.path.isdir(polib_path):
    try:
        print 'Cloning polib...'
        cmd_status = subprocess.check_output(
            'hg clone https://bitbucket.org/izi/polib/ %s -u 1.0.7' % polib_path,
            stderr=subprocess.STDOUT,
            shell=True)
        print cmd_status
    except Exception as e:
        print e
sys.path.append(os.path.join(polib_path))
try:
    import polib
except ImportError:
    print 'Error importing polib library'
    sys.exit(1)


def create_file_list(repo_folder, locale, source_pattern):
    ''' Search for files to analyze '''

    # Get a list of all reference files, since source_pattern can use wildcards
    locale_files = glob.glob(
        os.path.join(repo_folder, locale, source_pattern)
    )
    locale_files.sort()

    return locale_files


def analyze_files(repo_folder, locale, source_pattern):
    ''' Analyze files, returning an array with stats and errors '''

    global_stats = {}

    # Get a list of all files for the reference locale
    locale_files = create_file_list(repo_folder, locale, source_pattern)
    for locale_file in locale_files:
        fuzzy = 0
        total = 0
        translated = 0
        untranslated = 0
        try:
            po = polib.pofile(locale_file)
            fuzzy = len(po.fuzzy_entries())
            translated = len(po.translated_entries())
            untranslated = len(po.untranslated_entries())
        except Exception as e:
            print e
            sys.exit(1)

        total = translated + untranslated + fuzzy
        source_index = os.path.basename(locale_file)
        global_stats[source_index] = {
            'fuzzy': fuzzy,
            'total': total,
            'translated': translated,
            'untranslated': untranslated
        }

    return global_stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo_folder', help='Path to repository')
    parser.add_argument(
        'source_pattern', help='Source file pattern (wildcards are supported)')
    parser.add_argument('locale', help='Locale code to analyze')
    parser.add_argument('--pretty', action='store_true',
                        help='export indented and more readable JSON')
    args = parser.parse_args()

    global_stats = analyze_files(
        args.repo_folder, args.locale, args.source_pattern)

    if args.pretty:
        print json.dumps(global_stats, sort_keys=True, indent=2)
    else:
        print json.dumps(global_stats)


if __name__ == '__main__':
    main()
