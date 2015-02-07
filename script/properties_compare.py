#! /usr/bin/env python

import argparse
import json
import os
import subprocess
import sys

# Import Silme library (http://hg.mozilla.org/l10n/silme/)
silmepath = os.path.join(
    os.path.abspath(os.path.join(sys.path[0], os.pardir)),
    'libraries',
    'silme'
)

if not os.path.isdir(silmepath):
    try:
        print 'Cloning silme...'
        cmd_status = subprocess.check_output(
                    'hg clone http://hg.mozilla.org/l10n/silme libraries/silme -u silme-0.8.0',
                    stderr = subprocess.STDOUT,
                    shell = True)
        print cmd_status
    except Exception as e:
        print e

sys.path.append(os.path.join(silmepath, 'lib'))

import silme.core
import silme.io
import silme.format

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source_path', help="Path to source files")
    parser.add_argument('locale_path', help="Path to localized files")
    args = parser.parse_args()

    translated = 0
    missing = 0
    identical = 0

    try:
        silme.format.Manager.register('properties')
        rcs_client_source = silme.io.Manager.get('file')
        l10n_package_source = rcs_client_source.get_package(args.source_path, object_type='entitylist')
        rcs_client_locale = silme.io.Manager.get('file')
        l10n_package_locale = rcs_client_locale.get_package(args.locale_path, object_type='entitylist')

        source_entities = {}
        for item in l10n_package_source:
            if type(item[1]) is not silme.core.structure.Blob:
                for entity in item[1]:
                    source_entities[entity] = item[1][entity].get_value()

        for item in l10n_package_locale:
            if type(item[1]) is not silme.core.structure.Blob:
                for entity in source_entities:
                    if entity in item[1]:
                        if source_entities[entity] == item[1][entity].get_value():
                            identical += 1
                        else:
                            translated += 1
                    else:
                        missing += 1
    except Exception as e:
        print e

    json_data = {
        'identical': identical,
        'translated': translated,
        'missing': missing
    }
    print json.dumps(json_data, sort_keys=True)


if __name__ == '__main__':
    main()
