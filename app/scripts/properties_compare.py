#! /usr/bin/env python

import argparse
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source_file', help="Path to source files")
    parser.add_argument('locale_file', help="Path to localized files")
    args = parser.parse_args()

    translated = 0
    missing = 0
    identical = 0
    total = 0

    try:
        silme.format.Manager.register('properties')
        ioclient = silme.io.Manager.get('file')
        entities_source = ioclient.get_entitylist(args.source_file)
        entities_locale = ioclient.get_entitylist(args.locale_file)

        # Store reference strings
        source_strings = {}
        for entity in entities_source:
            source_strings[entity] = entities_source[entity].get_value()

        # Store translations
        locale_strings = {}
        for entity in entities_locale:
            locale_strings[entity] = entities_locale[entity].get_value()

        for entity in source_strings:
            if entity in locale_strings:
                translated += 1
                if source_strings[entity] == locale_strings[entity]:
                    identical += 1
            else:
                missing += 1
    except Exception as e:
        print e
        sys.exit(1)

    total = translated + missing
    json_data = {
        "identical": identical,
        "missing": missing,
        "total": total,
        "translated": translated
    }
    print json.dumps(json_data)


if __name__ == '__main__':
    main()
