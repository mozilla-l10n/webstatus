#! /usr/bin/env python

import argparse
import json
import sys
from xml.dom import minidom

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source_path', help='Path to XLIFF file')
    args = parser.parse_args()

    translated = 0
    missing = 0
    identical = 0

    try:
        xmldoc = minidom.parse(args.source_path)
        trans_units = xmldoc.getElementsByTagName('trans-unit')
        for trans_unit in trans_units:
            source = trans_unit.getElementsByTagName('source')
            target = trans_unit.getElementsByTagName('target')

            # Check if we have at least one source
            if not source:
                error_message = 'Trans unit %s is missing a <source> element' \
                                % trans_unit.attributes['id'].value
                raise ValueError(error_message)

            # Check if there are multiple source/target elements
            if len(source) > 1:
                error_message = 'Trans unit %s has multiple <source> elements' \
                                % trans_unit.attributes['id'].value
                raise ValueError(error_message)
            if len(target) > 1:
                error_message = 'Trans unit %s has multiple <target> elements' \
                                % trans_unit.attributes['id'].value
                raise ValueError(error_message)

            # Compare strings
            source_string = source[0].firstChild.data
            if target:
                target_string = target[0].firstChild.data
                translated += 1
                if source_string == target_string:
                    identical += 1
            else:
                missing += 1

        # If we have translations, check if files are missing a target-language
        if translated + identical > 1:
            file_elements = xmldoc.getElementsByTagName('file')
            for file_element in file_elements:
                if 'target-language' not in file_element.attributes.keys():
                    error_message = 'File %s is missing target-language attribute' \
                                    % file_element.attributes['original'].value
                    raise ValueError(error_message)
    except Exception as e:
        print e
        sys.exit(1)

    json_data = {
        "identical": identical,
        "translated": translated,
        "missing": missing
    }
    print json.dumps(json_data)


if __name__ == '__main__':
    main()
