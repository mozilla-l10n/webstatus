#! /usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import subprocess
import sys
from xml.dom import minidom

# Import local libraries
library_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir, 'libraries'))

# Silme library (http://hg.mozilla.org/l10n/silme/)
silme_path = os.path.join(library_path, 'silme')
if not os.path.isdir(silme_path):
    try:
        print 'Cloning silme...'
        cmd_status = subprocess.check_output(
            ['hg', 'clone', 'https://hg.mozilla.org/l10n/silme',
                silme_path, '-u', 'silme-0.8.0'],
            stderr=subprocess.STDOUT,
            shell=False)
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

# Polib library (https://bitbucket.org/izi/polib)
polib_path = os.path.join(library_path, 'polib')
if not os.path.isdir(polib_path):
    try:
        print 'Cloning polib...'
        cmd_status = subprocess.check_output(
            ['hg', 'clone', 'https://bitbucket.org/izi/polib',
                polib_path, '-u', '1.0.7'],
            stderr=subprocess.STDOUT,
            shell=False)
        print cmd_status
    except Exception as e:
        print e
sys.path.append(os.path.join(polib_path))
try:
    import polib
except ImportError:
    print 'Error importing polib library'
    sys.exit(1)


class Parser():
    '''Generic class used to analyze a source file pattern'''

    def create_file_list(self, repo_folder, locale, search_pattern):
        ''' Create a list of all files to analyze '''

        # Get a list of all files to analyze, since pattern can use wildcards
        locale_files = glob.glob(
            os.path.join(repo_folder, locale, search_pattern)
        )
        locale_files.sort()

        return locale_files

    def list_diff(self, a, b):
        ''' Return list of elements of list a not available in list b '''

        b = set(b)
        return [aa for aa in a if aa not in b]


class GettextParser(Parser):
    ''' Class to parse gettext files (.po) '''

    def __init__(self, repo_folder, search_pattern, locale):
        ''' Initialize parameters '''
        # Locale I'm analyzing
        self.locale = locale

        # Path to the repository
        self.repo_folder = repo_folder

        # Search pattern
        self.search_pattern = search_pattern

    def analyze_files(self):
        ''' Analyze files, returning an array with stats and errors '''

        global_stats = {}

        # Get a list of all files for the reference locale
        locale_files = self.create_file_list(
            self.repo_folder, self.locale, self.search_pattern)

        for locale_file in locale_files:
            fuzzy = 0
            total = 0
            translated = 0
            untranslated = 0
            try:
                po = polib.pofile(locale_file)
                obsolete_strings = po.obsolete_entries()
                # I need to exclude obsolete strings
                fuzzy = len(self.list_diff(
                    po.fuzzy_entries(), obsolete_strings))
                translated = len(self.list_diff(
                    po.translated_entries(), obsolete_strings))
                untranslated = len(self.list_diff(
                    po.untranslated_entries(), obsolete_strings))
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


class PropertiesParser(Parser):
    ''' Class to parse properties files (.properties) '''

    def __init__(self, repo_folder, search_pattern, reference, locale):
        ''' Initialize parameters '''
        # Path to the repository
        self.repo_folder = repo_folder

        # Search pattern
        self.search_pattern = search_pattern

        # Reference folder/locale for this product
        self.reference = reference

        # Locale I'm analyzing
        self.locale = locale

    def analyze_files(self):
        ''' Analyze files, returning an array with stats and errors '''

        try:
            silme.format.Manager.register('properties')
            ioclient = silme.io.Manager.get('file')
        except Exception as e:
            print e
            sys.exit(1)

        global_stats = {}

        # Get a list of all files for the reference locale
        reference_files = self.create_file_list(
            self.repo_folder, self.reference, self.search_pattern)
        for reference_file in reference_files:
            translated = 0
            missing = 0
            identical = 0
            total = 0
            try:
                locale_file = reference_file.replace(
                    '/{0}/'.format(self.reference),
                    '/{0}/'.format(self.locale)
                )
                reference_entities = ioclient.get_entitylist(reference_file)
                # Store reference strings
                reference_strings = {}
                for entity in reference_entities:
                    reference_strings[entity] = reference_entities[
                        entity].get_value()

                locale_strings = {}
                if os.path.isfile(locale_file):
                    # Locale file exists
                    missing_file = False
                    locale_entities = ioclient.get_entitylist(locale_file)

                    # Store translations
                    for entity in locale_entities:
                        locale_strings[entity] = locale_entities[
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
                    missing += len(reference_entities)
                    missing_file = True

            except Exception as e:
                print e
                sys.exit(1)

            # Check missing/obsolete strings
            missing_strings = self.list_diff(reference_strings, locale_strings)
            obsolete_strings = self.list_diff(
                locale_strings, reference_strings)

            total = translated + missing
            source_index = os.path.basename(reference_file)
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


class XliffParser(Parser):
    ''' Class to parse XLIFF files (.xliff) '''

    def __init__(self, repo_folder, search_pattern, reference, locale):
        ''' Initialize parameters '''

        # Path to the repository
        self.repo_folder = repo_folder

        # Search pattern
        self.search_pattern = search_pattern

        # Reference folder/locale for this product
        self.reference = reference

        # Locale I'm analyzing
        self.locale = locale

    def analyze_files(self):
        ''' Analyze files, returning an array with stats and errors '''

        global_stats = {}

        # Get a list of all files for the reference locale
        source_files = self.create_file_list(
            self.repo_folder, self.reference, self.search_pattern)
        for source_file in source_files:
            reference_strings = []
            reference_stats = self.parse_xliff(
                source_file,
                reference_strings,
                []
            )

            locale_strings = []
            untranslated_strings = []
            locale_file = source_file.replace(
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
                    'errors': 'File {0} is missing'.format(os.path.basename(locale_file)),
                    'identical': 0,
                    'total': 0,
                    'translated': 0,
                    'untranslated': 0
                }

            # Check missing/obsolete strings
            missing_strings = self.list_diff(reference_strings, locale_strings)
            obsolete_strings = self.list_diff(
                locale_strings, reference_strings)

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
                string_id = u'{0}:{1}'.format(
                    file_element_name, trans_unit.attributes['id'].value)
                string_list.append(string_id)

                # Check if we have at least one source
                if not source:
                    error_msg = u'Trans unit “{0}” in file ”{1}” is missing a <source> element'.format(
                        trans_unit.attributes['id'].value, file_element_name)
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
                        error_msg = u'Trans unit “{0}” in file ”{1}” has multiple <source> elements'.format(
                            trans_unit.attributes['id'].value, file_element_name)
                        errors.append(error_msg)
                if len(target) > 1:
                    target_count = 0
                    for target_element in target:
                        if target_element.parentNode.tagName != 'alt-trans':
                            target_count += 1
                    if target_count > 1:
                        error_msg = u'Trans unit “{0}” in file ”{1}” has multiple <target> elements'.format(
                            trans_unit.attributes['id'].value, file_element_name)
                        errors.append(error_msg)

                # Compare strings
                try:
                    source_string = source[0].firstChild.data
                except:
                    error_msg = u'Trans unit “{0}” in file ”{1}” has a malformed or empty <source> element'.format(
                        trans_unit.attributes['id'].value, file_element_name)
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
                        error_msg = u'File “{0}” is missing target-language attribute'.format(
                            file_element.attributes['original'].value)
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
