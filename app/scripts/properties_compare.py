#! /usr/bin/env python

import argparse
import glob
import json
import os
import subprocess
import sys

# Import Silme library (http://hg.mozilla.org/l10n/silme/)
silmepath = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)),
    'libraries',
    'silme'
)

if not os.path.isdir(silmepath):
    try:
        print 'Cloning silme...'
        cmd_status = subprocess.check_output(
            'hg clone http://hg.mozilla.org/l10n/silme %s -u silme-0.8.0' % silmepath,
            stderr=subprocess.STDOUT,
            shell=True)
        print cmd_status
    except Exception as e:
        print e

sys.path.append(os.path.join(silmepath, 'lib'))

import silme.core
import silme.io
import silme.format


def diff(a, b):
    b = set(b)
    return [aa for aa in a if aa not in b]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo_folder', help='Path to repository')
    parser.add_argument(
        'source_file', help='Source file (wildcards are supported)')
    parser.add_argument('reference', help='Reference locale code')
    parser.add_argument('locale', help='Locale code to analyze')
    parser.add_argument('--pretty', action='store_true',
                        help='export indented and more readable JSON')
    args = parser.parse_args()

    # Get a list of all reference files, since source_files can use wildcards
    source_files = glob.glob(
        os.path.join(args.repo_folder, args.reference, args.source_file)
    )
    source_files.sort()

    try:
        silme.format.Manager.register('properties')
        ioclient = silme.io.Manager.get('file')
    except Exception as e:
        print e
        sys.exit(1)

    global_stats = {}
    for source_file in source_files:
        translated = 0
        missing = 0
        identical = 0
        total = 0
        try:
            locale_file = source_file.replace(
                '/%s/' % args.reference,
                '/%s/' % args.locale
            )
            entities_reference = ioclient.get_entitylist(source_file)

            if os.path.isfile(locale_file):
                # Locale file exists
                entities_locale = ioclient.get_entitylist(locale_file)

                # Store reference strings
                reference_strings = {}
                for entity in entities_reference:
                    reference_strings[entity] = entities_reference[
                        entity].get_value()

                # Store translations
                locale_strings = {}
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
                reference_strings = []
                locale_strings = []

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
            'missing_strings': missing_strings,
            'obsolete': len(obsolete_strings),
            'obsolete_strings': obsolete_strings,
            'total': total,
            'translated': translated
        }

    if args.pretty:
        print json.dumps(global_stats, sort_keys=True, indent=2)
    else:
        print json.dumps(global_stats)


if __name__ == '__main__':
    main()
