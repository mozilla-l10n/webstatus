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
    total = 0

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
                # Exclude elements in alt-trans nodes
                source_count = 0
                for source_element in source:
                    if source_element.parentNode.tagName != 'alt-trans':
                        source_count += 1
                if source_count > 1:
                    error_message = 'Trans unit %s has multiple <source> elements' \
                                    % trans_unit.attributes['id'].value
                    raise ValueError(error_message)
            if len(target) > 1:
                target_count = 0
                for target_element in target:
                    if target_element.parentNode.tagName != 'alt-trans':
                        target_count += 1
                if target_count > 1:
                    error_message = 'Trans unit %s has multiple <target> elements' \
                                    % trans_unit.attributes['id'].value
                    raise ValueError(error_message)

            # Compare strings
            try:
                source_string = source[0].firstChild.data
            except:
                error_message = 'Trans unit %s has a malformed <source> element' \
                                % trans_unit.attributes['id'].value
                raise ValueError(error_message)
            if target:
                try:
                    source_string = source[0].firstChild.data
                    target_string = target[0].firstChild.data
                    translated += 1
                    if source_string == target_string:
                        identical += 1
                except:
                    error_message = 'Trans unit %s has a malformed <target> element' \
                                    % trans_unit.attributes['id'].value
                    raise ValueError(error_message)
            else:
                missing += 1

        # If we have translations, check if the first file is missing a target-language
        if translated + identical > 1:
            file_elements = xmldoc.getElementsByTagName('file')
            if len(file_elements) > 0:
                file_element = file_elements[0]
                if 'target-language' not in file_element.attributes.keys():
                    error_message = 'File %s is missing target-language attribute' \
                                    % file_element.attributes['original'].value
                    raise ValueError(error_message)
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
