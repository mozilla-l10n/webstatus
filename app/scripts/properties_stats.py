#! /usr/bin/env python

import argparse
import glob
import json
import os
import subprocess
import sys

# Import local libraries
app_folder = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir))

# Silme library (http://hg.mozilla.org/l10n/silme/)
silme_path = os.path.join(app_folder, 'libraries', 'silme')
if not os.path.isdir(silme_path):
    try:
        print 'Cloning silme...'
        cmd_status = subprocess.check_output(
            'hg clone https://hg.mozilla.org/l10n/silme %s -u silme-0.8.0' % silme_path,
            stderr=subprocess.STDOUT,
            shell=True)
        print cmd_status
    except Exception as e:
        print e
sys.path.append(os.path.join(silme_path, 'lib'))
try:
    import silme.core
    import silme.io
    import silme.format
except ImportError:
    print 'Error importing Silme library'
    sys.exit(1)


def diff(a, b):
    b = set(b)
    return [aa for aa in a if aa not in b]


def create_file_list(repo_folder, reference, source_pattern):
    ''' Search for files to analyze '''

    # Get a list of all reference files, since source_pattern can use wildcards
    source_files = glob.glob(
        os.path.join(repo_folder, reference, source_pattern)
    )
    source_files.sort()

    return source_files


def analyze_files(repo_folder, locale, reference, source_pattern):
    ''' Analyze files, returning an array with stats and errors '''

    try:
        silme.format.Manager.register('properties')
        ioclient = silme.io.Manager.get('file')
    except Exception as e:
        print e
        sys.exit(1)

    global_stats = {}

    # Get a list of all files for the reference locale
    source_files = create_file_list(repo_folder, reference, source_pattern)
    for source_file in source_files:
        translated = 0
        missing = 0
        identical = 0
        total = 0
        try:
            locale_file = source_file.replace(
                '/%s/' % reference,
                '/%s/' % locale
            )
            entities_reference = ioclient.get_entitylist(source_file)
            # Store reference strings
            reference_strings = {}
            for entity in entities_reference:
                reference_strings[entity] = entities_reference[
                    entity].get_value()

            locale_strings = {}
            if os.path.isfile(locale_file):
                # Locale file exists
                missing_file = False
                entities_locale = ioclient.get_entitylist(locale_file)

                # Store translations
                for entity in entities_locale:
                    locale_strings[entity] = entities_locale[
                        entity].get_value()

                for entity in reference_strings:
                    if entity in locale_strings:
                        translated += 1
                        if reference_strings[entity] == locale_strings[entity]:
                            identical += 1
                    else:
                        missing += 1
            else:
                # Locale file doesn't exist, count all reference strings as
                # missing
                missing += len(entities_reference)
                missing_file = True

        except Exception as e:
            print e
            sys.exit(1)

        # Check missing/obsolete strings
        missing_strings = diff(reference_strings, locale_strings)
        obsolete_strings = diff(locale_strings, reference_strings)

        total = translated + missing
        source_index = os.path.basename(source_file)
        global_stats[source_index] = {
            'identical': identical,
            'missing': missing,
            'missing_file': missing_file,
            'missing_strings': missing_strings,
            'obsolete': len(obsolete_strings),
            'obsolete_strings': obsolete_strings,
            'total': total,
            'translated': translated
        }

    return global_stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo_folder', help='Path to repository')
    parser.add_argument(
        'source_pattern', help='Source file pattern (wildcards are supported)')
    parser.add_argument('reference', help='Reference locale code')
    parser.add_argument('locale', help='Locale code to analyze')
    parser.add_argument('--pretty', action='store_true',
                        help='export indented and more readable JSON')
    args = parser.parse_args()

    global_stats = analyze_files(
        args.repo_folder, args.locale,
        args.reference, args.source_pattern)

    if args.pretty:
        print json.dumps(global_stats, sort_keys=True, indent=2)
    else:
        print json.dumps(global_stats)


if __name__ == '__main__':
    main()
