#! /usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import re
from xml.dom import minidom

# Import external libraries
import polib
from compare_locales import parser as comparelocales_parser

# Python 2/3 compatibility
import six
from six import iteritems


class Parser():
    '''Generic class used to analyze a source file pattern'''

    def create_file_list(self, repo_folder, locale, search_patterns):
        ''' Create a list of all files to analyze '''

        # Get a list of all files to analyze, since pattern can use wildcards
        locale_files = []
        for search_pattern in search_patterns:
            locale_files += glob.glob(
                os.path.join(repo_folder, locale, search_pattern)
            )
        locale_files.sort()

        return locale_files

    def list_diff(self, a, b):
        ''' Return list of elements of list a not available in list b '''

        b = set(b)
        return [aa for aa in a if aa not in b]

    def set_locale(self, locale):
        ''' Set current locale '''

        self.locale = locale

    def count_words(self, text):
        '''Taken from compare-locales'''
        re_br = re.compile('<br[ \t\r\n]*/?>', re.U)
        re_sgml = re.compile(r'</?\w+.*?>', re.U | re.M)

        text = re_br.sub(u'\n', text)
        text = re_sgml.sub(u'', text)
        return len(text.split())


class GettextParser(Parser):
    ''' Class to parse gettext files (.po) '''

    def __init__(self, repo_folder, search_patterns):
        # Path to the repository
        self.repo_folder = repo_folder

        # Search pattern
        self.search_patterns = search_patterns

    def analyze_files(self):
        ''' Analyze files, returning an array with stats and errors '''

        global_stats = {}

        # Get a list of all files for the reference locale
        locale_files = self.create_file_list(
            self.repo_folder, self.locale, self.search_patterns)

        for locale_file in locale_files:
            fuzzy = 0
            total = 0
            total_w = 0
            translated = 0
            untranslated = 0
            errors = []
            try:
                po = polib.pofile(locale_file)
                obsolete_strings = po.obsolete_entries()
                # I need to exclude obsolete strings
                fuzzy = len(self.list_diff(
                    po.fuzzy_entries(), obsolete_strings))
                for entry in po.fuzzy_entries():
                    total_w += self.count_words(entry.msgid)

                translated = len(self.list_diff(
                    po.translated_entries(), obsolete_strings))
                for entry in po.translated_entries():
                    total_w += self.count_words(entry.msgid)

                untranslated = len(self.list_diff(
                    po.untranslated_entries(), obsolete_strings))
                for entry in po.untranslated_entries():
                    total_w += self.count_words(entry.msgid)
            except Exception as e:
                errors.append(str(e))

            total = translated + untranslated + fuzzy
            source_index = os.path.basename(locale_file)
            global_stats[source_index] = {
                'errors': '\n'.join(errors),
                'fuzzy': fuzzy,
                'total': total,
                'total_w': total_w,
                'translated': translated,
                'untranslated': untranslated
            }

        return global_stats


class PropertiesFTLParser(Parser):
    ''' Class to parse properties (.properties) and FTL (.ftl) files '''

    def __init__(self, repo_folder, search_patterns, reference):
        ''' Initialize parameters '''
        # Path to the repository
        self.repo_folder = repo_folder

        # Search pattern
        self.search_patterns = search_patterns

        # Reference folder/locale for this product
        self.reference = reference

        # Store reference data to read them only once
        self.reference_strings = {}
        self.reference_files = []

    def analyze_files(self):
        ''' Analyze files, returning an array with stats and errors '''

        # Create a list of reference files, and store reference data only once.
        # Object has the following structure:
        #
        # {
        #     'filename1': {
        #         'entity1': 'value1',
        #         ...
        #     },
        #     ...
        # }
        global_stats = {}

        if not self.reference_files:
            self.reference_files = self.create_file_list(
                self.repo_folder, self.reference, self.search_patterns)
            for reference_file in self.reference_files:
                # Parser can be for .ftl or .properties
                file_type = os.path.splitext(reference_file)[1]
                file_parser = comparelocales_parser.getParser(file_type)
                file_parser.readFile(reference_file)
                reference_entities = file_parser.parse()
                file_index = os.path.basename(reference_file)

                translations = {}
                for entity in reference_entities:
                    if isinstance(entity, comparelocales_parser.Junk):
                        continue

                    if file_type == '.ftl':
                        if entity.raw_val != '':
                            entity_name = six.text_type(entity)
                            translations[entity_name] = entity.raw_val
                        for attribute in entity.attributes:
                            entity_name = u'{0}.{1}'.format(entity, attribute)
                            translations[entity_name] = attribute.raw_val
                    else:
                        translations[six.text_type(entity)] = entity.raw_val
                self.reference_strings[file_index] = translations.copy()

        for reference_file in self.reference_files:
            file_index = os.path.basename(reference_file)
            translated = 0
            missing = 0
            identical = 0
            total = 0
            total_w = 0
            errors = []

            # Parser can be used for .ftl or .properties
            file_type = os.path.splitext(reference_file)[1]
            try:
                locale_file = reference_file.replace(
                    '/{0}/'.format(self.reference),
                    '/{0}/'.format(self.locale)
                )
                locale_strings = {}
                if os.path.isfile(locale_file):
                    # Locale file exists
                    missing_file = False
                    file_parser = comparelocales_parser.getParser(file_type)
                    file_parser.readFile(locale_file)
                    locale_entities = file_parser.parse()

                    # Store translations
                    for entity in locale_entities:
                        if isinstance(entity, comparelocales_parser.Junk):
                            errors.append(
                                u'Unparsed content: {0}, {1}'.format(
                                    entity, entity.val))
                        else:
                            # Use original count_words from compare_locales
                            total_w += entity.count_words()
                            if file_type == '.ftl':
                                if entity.raw_val != '':
                                    locale_strings[six.text_type(
                                        entity)] = entity.raw_val
                                for attribute in entity.attributes:
                                    entity_name = u'{0}.{1}'.format(
                                        entity, attribute)
                                    locale_strings[entity_name] = \
                                        attribute.raw_val
                            else:
                                locale_strings[six.text_type(
                                    entity)] = entity.raw_val
                    for entity, original in \
                            iteritems(self.reference_strings[file_index]):
                        if entity in locale_strings:
                            translated += 1
                            if locale_strings[entity] == original:
                                identical += 1
                        else:
                            missing += 1
                else:
                    # Locale file doesn't exist, count all reference strings as
                    # missing
                    missing += len(self.reference_strings[file_index])
                    missing_file = True

            except Exception as e:
                errors.append(str(e))

            # Check missing/obsolete strings
            missing_strings = self.list_diff(
                self.reference_strings[file_index], locale_strings)
            obsolete_strings = self.list_diff(
                locale_strings, self.reference_strings[file_index])
            # Ignore obsolete string attributes for .ftl
            if file_type == '.ftl':
                for s in obsolete_strings[:]:
                    if '.' in s:
                        main_id = s.split('.')[0]
                        if main_id not in missing_strings:
                            obsolete_strings.remove(s)

            total = translated + missing
            global_stats[file_index] = {
                'errors': '\n'.join(errors),
                'identical': identical,
                'missing': missing,
                'missing_file': missing_file,
                'missing_strings': missing_strings,
                'obsolete': len(obsolete_strings),
                'obsolete_strings': obsolete_strings,
                'total': total,
                'total_w': total_w,
                'translated': translated
            }

        return global_stats


class XliffParser(Parser):
    ''' Class to parse XLIFF files (.xliff) '''

    def __init__(self, repo_folder, search_patterns, reference):
        ''' Initialize parameters '''

        # Path to the repository
        self.repo_folder = repo_folder

        # Search pattern
        self.search_patterns = search_patterns

        # Reference folder/locale for this product
        self.reference = reference

        # Store reference data to read them only once
        self.reference_strings = {}
        self.reference_files = []

    def analyze_files(self):
        ''' Analyze files, returning an array with stats and errors '''

        global_stats = {}

        # Create a list of reference files, and store reference data only once.
        # Object has the following structure:
        #
        # {
        #     'filename': {
        #         'entity1': 'value1',
        #         ...
        #     ...
        # }
        if not self.reference_files:
            self.reference_files = self.create_file_list(
                self.repo_folder, self.reference, self.search_patterns)
            for reference_file in self.reference_files:
                file_index = os.path.basename(reference_file)
                self.reference_strings[file_index] = []
                self.parse_xliff(
                    reference_file,
                    self.reference_strings[file_index],
                    []
                )

        for reference_file in self.reference_files:
            file_index = os.path.basename(reference_file)
            locale_strings = []
            untranslated_strings = []
            locale_file = reference_file.replace(
                '/{0}/'.format(self.reference),
                '/{0}/'.format(self.locale)
            )

            if os.path.isfile(locale_file):
                locale_stats = self.parse_xliff(
                    locale_file,
                    locale_strings,
                    untranslated_strings
                )
            else:
                locale_stats = {
                    'errors': 'File {0} is missing'.format(file_index),
                    'identical': 0,
                    'total': 0,
                    'total_w': 0,
                    'translated': 0,
                    'untranslated': 0
                }

            # Check missing/obsolete strings
            missing_strings = self.list_diff(
                self.reference_strings[file_index], locale_strings)
            obsolete_strings = self.list_diff(
                locale_strings, self.reference_strings[file_index])

            global_stats[file_index] = {
                'errors': locale_stats['errors'],
                'identical': locale_stats['identical'],
                'missing': len(missing_strings),
                'missing_strings': missing_strings,
                'obsolete': len(obsolete_strings),
                'obsolete_strings': obsolete_strings,
                'total': locale_stats['total'],
                'total_w': locale_stats['total_w'],
                'translated': locale_stats['translated'],
                'untranslated': locale_stats['untranslated'],
                'untranslated_strings': untranslated_strings
            }

        return global_stats

    def parse_xliff(self, file_path, string_list, untranslated_strings):
        # This function parses a XLIFF file
        #
        # file_path: path to the XLIFF file to analyze
        # string_list: string IDs are stored in the form of fileunit:stringid
        # untranslated_strings: untranslated strings
        #
        # Returns a JSON record with stats about translations.
        #

        identical = 0
        total = 0
        total_w = 0
        translated = 0
        untranslated = 0
        errors = []

        try:
            xmldoc = minidom.parse(file_path)
            trans_units = xmldoc.getElementsByTagName('trans-unit')
            for trans_unit in trans_units:
                source = trans_unit.getElementsByTagName('source')
                target = trans_unit.getElementsByTagName('target')

                file_element_name = \
                    trans_unit.parentNode.parentNode.attributes[
                        'original'].value
                # Store the string ID
                string_id = u'{0}:{1}'.format(
                    file_element_name, trans_unit.attributes['id'].value)
                string_list.append(string_id)

                # Check if we have at least one source
                if not source:
                    error_msg = (
                        u'Trans unit “{0}” in file ”{1}”'
                        ' is missing a <source> element'.format(
                            trans_unit.attributes['id'].value,
                            file_element_name))
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
                        error_msg = (
                            u'Trans unit “{0}” in file ”{1}”'
                            ' has multiple <source> elements'.format(
                                trans_unit.attributes['id'].value,
                                file_element_name))
                        errors.append(error_msg)
                if len(target) > 1:
                    target_count = 0
                    for target_element in target:
                        if target_element.parentNode.tagName != 'alt-trans':
                            target_count += 1
                    if target_count > 1:
                        error_msg = (
                            u'Trans unit “{0}” in file ”{1}”'
                            ' has multiple <target> elements'.format(
                                trans_unit.attributes['id'].value,
                                file_element_name))
                        errors.append(error_msg)

                # Compare strings
                try:
                    source_string = source[0].firstChild.data
                    total_w += self.count_words(source_string)
                except Exception as e:
                    error_msg = (
                        u'Trans unit “{0}” in file ”{1}”'
                        ' has a malformed or empty <source> element'.format(
                            trans_unit.attributes['id'].value,
                            file_element_name))
                    errors.append(error_msg)
                    continue
                if target:
                    try:
                        target_string = target[0].firstChild.data
                    except Exception as e:
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
                        error_msg = (
                            u'File “{0}” is missing target-language'
                            ' attribute'.format(
                                file_element.attributes['original'].value))
                        errors.append(error_msg)
        except Exception as e:
            errors.append(str(e))

        total = translated + untranslated
        file_stats = {
            'errors': '\n'.join(errors),
            'identical': identical,
            'total': total,
            'total_w': total_w,
            'translated': translated,
            'untranslated': untranslated
        }

        return file_stats
