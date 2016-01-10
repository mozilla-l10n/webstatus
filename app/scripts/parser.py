#! /usr/bin/env python

import glob
import os
import subprocess
import sys

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
        ''' Check environment and initialize parameters '''
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
        ''' Check environment and initialize parameters '''
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
        reference_files = self.create_file_list(self.repo_folder, self.reference, self.search_pattern)
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
            obsolete_strings = self.list_diff(locale_strings, reference_strings)

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
