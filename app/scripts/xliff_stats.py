#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import glob
import json
import os
import sys
from xml.dom import minidom


def analyze_file(file_path, string_list, untranslated_strings):
    # This function parses a XLIFF file
    #
    # file_path: path to the XLIFF file to analyze
    # string_list: string IDs are stored in the form of fileunit:stringid
    # untranslated_strings: untranslated strings
    #
    # Returns a JSON record with stats about translations.
    #

    identical = 0
    missing = 0
    total = 0
    translated = 0
    untranslated = 0
    errors = []

    try:
        xmldoc = minidom.parse(file_path)
        trans_units = xmldoc.getElementsByTagName('trans-unit')
        for trans_unit in trans_units:
            source = trans_unit.getElementsByTagName('source')
            target = trans_unit.getElementsByTagName('target')

            file_element_name = trans_unit.parentNode.parentNode.attributes[
                'original'].value
            # Store the string ID
            string_id = '%s:%s' % \
                        (file_element_name, trans_unit.attributes['id'].value)
            string_list.append(string_id)

            # Check if we have at least one source
            if not source:
                error_msg = u'Trans unit “%s” in file ”%s” is missing a <source> element' \
                            % (trans_unit.attributes['id'].value, file_element_name)
                errors.append(error_msg)
                continue

            # Check if there are multiple source/target elements
            if len(source) > 1:
                # Exclude elements in alt-trans nodes
                source_count = 0
                for source_element in source:
                    if source_element.parentNode.tagName != 'alt-trans':
                        source_count += 1
                if source_count > 1:
                    error_msg = u'Trans unit “%s” in file ”%s” has multiple <source> elements' \
                                % (trans_unit.attributes['id'].value, file_element_name)
                    errors.append(error_msg)
            if len(target) > 1:
                target_count = 0
                for target_element in target:
                    if target_element.parentNode.tagName != 'alt-trans':
                        target_count += 1
                if target_count > 1:
                    error_msg = u'Trans unit “%s” in file ”%s” has multiple <target> elements' \
                                % (trans_unit.attributes['id'].value, file_element_name)
                    errors.append(error_msg)

            # Compare strings
            try:
                source_string = source[0].firstChild.data
            except:
                error_msg = u'Trans unit “%s” in file ”%s” has a malformed or empty <source> element' \
                            % (trans_unit.attributes['id'].value, file_element_name)
                errors.append(error_msg)
                continue
            if target:
                try:
                    target_string = target[0].firstChild.data
                except:
                    target_string = ''
                translated += 1
                if source_string == target_string:
                    identical += 1
            else:
                untranslated_strings.append(string_id)
                untranslated += 1

        # If we have translations, check if the first file is missing a
        # target-language
        if translated + identical > 1:
            file_elements = xmldoc.getElementsByTagName('file')
            if len(file_elements) > 0:
                file_element = file_elements[0]
                if 'target-language' not in file_element.attributes.keys():
                    error_msg = u'File “%s” is missing target-language attribute' \
                                % file_element.attributes['original'].value
                    errors.append(error_msg)
    except Exception as e:
        print e
        sys.exit(1)

    total = translated + untranslated
    file_stats = {
        'errors': '\n'.join(errors),
        'identical': identical,
        'total': total,
        'translated': translated,
        'untranslated': untranslated
    }

    return file_stats


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

    global_stats = {}

    # Get a list of all files for the reference locale
    source_files = create_file_list(repo_folder, reference, source_pattern)
    for source_file in source_files:
        reference_strings = []
        reference_stats = analyze_file(
            source_file,
            reference_strings,
            []
        )

        locale_strings = []
        untranslated_strings = []
        locale_file = source_file.replace(
            '/%s/' % reference,
            '/%s/' % locale
        )

        if os.path.isfile(locale_file):
            locale_stats = analyze_file(
                locale_file,
                locale_strings,
                untranslated_strings
            )
        else:
            locale_stats = {
                'errors': 'File %s is missing' % os.path.basename(locale_file),
                'identical': 0,
                'total': 0,
                'translated': 0,
                'untranslated': 0
            }

        # Check missing/obsolete strings
        missing_strings = diff(reference_strings, locale_strings)
        obsolete_strings = diff(locale_strings, reference_strings)

        source_index = os.path.basename(source_file)
        global_stats[source_index] = {
            'errors': locale_stats['errors'],
            'identical': locale_stats['identical'],
            'missing': len(missing_strings),
            'missing_strings': missing_strings,
            'obsolete': len(obsolete_strings),
            'obsolete_strings': obsolete_strings,
            'total': locale_stats['total'],
            'translated': locale_stats['translated'],
            'untranslated': locale_stats['untranslated'],
            'untranslated_strings': untranslated_strings
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
