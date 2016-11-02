#! /usr/bin/env python

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
from ConfigParser import SafeConfigParser
from StringIO import StringIO
from datetime import datetime

# Import local libraries
import parser


class FileAnalysis():
    '''Class used to analyze a source file pattern'''

    def __init__(self, source_type, storage_path):
        '''Initialize object with only source type, make sure file_parse is not defined'''

        self.file_parser = None
        self.source_type = source_type
        self.storage_path = storage_path

    def set_product_folder(self, product_folder):
        ''' Set product folder '''

        self.product_folder = product_folder

    def set_locale(self, locale):
        ''' Set current locale '''

        self.locale = locale

    def set_reference(self, reference):
        ''' Set reference locale/folder '''

        self.reference = reference

    def set_search_patterns(self, search_patterns):
        ''' Set file search patterns '''

        self.search_patterns = search_patterns

    def analyze_pattern(self):
        '''Initialize internal stats and call the specific method to perform the actual analysis'''

        # Initialize stats
        self.__initialize_stats()
        # Pick the correct analysis based on source_type
        if self.source_type == 'gettext':
            if self.file_parser is None:
                self.file_parser = parser.GettextParser(
                    self.product_folder, self.search_patterns)
            self.file_parser.set_locale(self.locale)
            self.__analyze_gettext()
        elif self.source_type == 'properties':
            if self.file_parser is None:
                self.file_parser = parser.PropertiesParser(
                    self.product_folder, self.search_patterns, self.reference)
            self.file_parser.set_locale(self.locale)
            self.__analyze_properties()
        elif self.source_type == 'xliff':
            if self.file_parser is None:
                self.file_parser = parser.XliffParser(
                    self.product_folder, self.search_patterns, self.reference)
            self.file_parser.set_locale(self.locale)
            self.__analyze_xliff()

        return self.__calculate_stats()

    def __analyze_gettext(self):
        '''Analyze gettext (.po) files'''

        try:
            string_stats_json = self.file_parser.analyze_files()
            for file_name, file_data in string_stats_json.iteritems():
                self.string_count['fuzzy'] += file_data['fuzzy']
                self.string_count['translated'] += file_data['translated']
                self.string_count[
                    'untranslated'] += file_data['untranslated']
                self.string_count['total'] += file_data['total']
                if file_data['errors'] != '':
                    # Hide storage path from polib error messages
                    error_msg = file_data['errors'].replace(
                        self.storage_path, '')
                    self.error_record[
                        'messages'] = u'Error extracting stats: {0!s}\n'.format(error_msg)
        except Exception as e:
            print('\n' + e)
            self.error_record[
                'messages'] = 'Generic error extracting stats.\n'

        if self.error_record['messages']:
            self.error_record['status'] = True

    def __analyze_properties(self):
        ''' Analyze properties files '''

        try:
            string_stats_json = self.file_parser.analyze_files()
            for file_name, file_data in string_stats_json.iteritems():
                self.string_count['identical'] += file_data['identical']
                self.string_count['missing'] += file_data['missing']
                self.string_count['translated'] += file_data['translated']
                self.string_count['total'] += file_data['total']
                if file_data['errors'] != '':
                    self.error_record[
                        'messages'] = u'Error extracting stats: {0!s}\n'.format(file_data['errors'])
        except subprocess.CalledProcessError as e:
            print('\n' + e)
            self.error_record[
                'messages'] = 'Error extracting stats: {0!s}\n'.format(e.output)
        except Exception as e:
            print('\n' + e)
            self.error_record[
                'messages'] = 'Generic error extracting stats.\n'

        if self.error_record['messages']:
            self.error_record['status'] = True

    def __analyze_xliff(self):
        ''' Analyze XLIFF files '''

        try:
            string_stats_json = self.file_parser.analyze_files()
            for file_name, file_data in string_stats_json.iteritems():
                self.string_count['identical'] += file_data['identical']
                self.string_count['missing'] += file_data['missing']
                self.string_count['translated'] += file_data['translated']
                self.string_count[
                    'untranslated'] += file_data['untranslated']
                self.string_count['total'] += file_data['total']
                if file_data['errors'] != '':
                    self.error_record[
                        'messages'] = u'Error extracting stats: {0!s}\n'.format(file_data['errors'])
        except Exception as e:
            print('\n' + e)
            self.error_record[
                'messages'] = 'Generic error extracting stats.\n'

        if self.error_record['messages']:
            self.error_record['status'] = True

    def __calculate_stats(self):
        ''' Generate a full status record with stats '''

        percentage = 0

        # Calculate stats
        if (self.string_count['total'] == 0 and not self.error_record['status']):
            # This locale has 0 strings (it might happen for a project with
            # .properties files and an empty folder)
            complete = False
            percentage = 0
        elif (self.string_count['fuzzy'] == 0 and
                self.string_count['missing'] == 0 and
                self.string_count['untranslated'] == 0):
            # No untranslated, missing or fuzzy strings, locale is complete
            complete = True
            percentage = 100
        elif self.string_count['missing'] > 0:
            complete = False
            percentage = round((float(self.string_count['translated']) / (
                self.string_count['total'] + self.string_count['missing'])) * 100, 1)
        else:
            # Need to calculate the level of completeness
            complete = False
            percentage = round(
                (float(self.string_count['translated']) / self.string_count['total']) * 100, 1)

        return {
            'complete': complete,
            'error_message': self.error_record['messages'],
            'error_status': self.error_record['status'],
            'fuzzy': self.string_count['fuzzy'],
            'identical': self.string_count['identical'],
            'missing': self.string_count['missing'],
            'percentage': percentage,
            'total': self.string_count['total'],
            'translated': self.string_count['translated'],
            'source_type': self.source_type,
            'untranslated': self.string_count['untranslated']
        }

    def __initialize_stats(self):
        '''Initialize error status and stats'''

        # Initialize error status
        self.error_record = {
            'status': False,
            'messages': ''
        }

        # Initialize string counters
        self.string_count = {
            'fuzzy': 0,
            'identical': 0,
            'missing': 0,
            'translated': 0,
            'untranslated': 0,
            'total': 0
        }


class Repositories():
    '''Class used to manage repositories'''

    def __init__(self, storage_path, noupdates):
        '''
            Initialize object parameters like storage path and if
            repositories need to be updated.
        '''

        self.storage_path = storage_path
        self.updates_disabled = noupdates

    def check_repo(self, product):
        ''' Clone or update the repository for the current product '''

        self.__set_product(product)
        if os.path.isdir(self.path):
            # Folder exists, check if it's actually a repository by searching
            # for .git, .hg, .svn in the root
            hidden_folder = '.{0}'.format(self.type)
            if os.path.isdir(os.path.join(self.path, hidden_folder)):
                # Update existing repository, only if needed
                if not self.updates_disabled:
                    self.__update_repo()
            else:
                # It's not a repository: delete folder and re-clone
                print(
                    'Removing folder (not a valid repository): {0}'.format(self.path))
                shutil.rmtree(self.path)
                self.__clone_repo()
        else:
            # Repository doesn't exist, need to clone it
            self.__clone_repo()

    def __clone_repo(self):
        ''' Clone product's repository '''

        # Move in the main storage path
        os.chdir(self.storage_path)
        print('Cloning repository: {0}'.format(self.url))
        if (self.type == 'git'):
            # git repository
            try:
                cmd_status = subprocess.check_output(
                    ['git', 'clone', '--depth', '1', self.url, self.name],
                    stderr=subprocess.STDOUT,
                    shell=False)
                print(cmd_status)
            except Exception as e:
                print(e)
        else:
            # svn repository
            try:
                cmd_status = subprocess.check_output(
                    ['svn', 'co', self.url, self.name],
                    stderr=subprocess.STDOUT,
                    shell=False)
                print(cmd_status)
            except Exception as e:
                print(e)

    def __set_product(self, product):
        ''' Set product information '''

        self.displayed_name = product['displayed_name']
        self.name = product['repository_name']
        self.path = os.path.join(self.storage_path, self.name)
        self.type = product['repository_type']
        self.url = product['repository_url']

    def __update_repo(self):
        ''' Update existing product's repository '''

        # Move in the repository folder
        os.chdir(self.path)
        print('Updating repository: {0}'.format(self.displayed_name))
        if (self.type == 'git'):
            # git repository
            try:
                cmd_status = subprocess.check_output(
                    ['git', 'pull'],
                    stderr=subprocess.STDOUT,
                    shell=False)
                print(cmd_status)
            except Exception as e:
                print(e)
        else:
            # svn repository
            try:
                cmd_status = subprocess.check_output(
                    ['svn', 'up'],
                    stderr=subprocess.STDOUT,
                    shell=False)
                print(cmd_status)
            except Exception as e:
                print(e)


def check_environment(main_path, settings):
    env_errors = False

    # Check if config file exists and parse it
    config_file = os.path.join(main_path, 'app', 'config', 'config.ini')
    if not os.path.isfile(config_file):
        print('Configuration file (app/config/config.ini) is missing.')
        env_errors = True
    else:
        try:
            ini_parser = SafeConfigParser()
            ini_parser.readfp(open(config_file))
            settings['storage_path'] = ini_parser.get('config', 'storage_path')
            if not os.path.isdir(settings['storage_path']):
                print('Folder specified in config.ini is missing ({0}).'.format(
                    settings['storage_path']))
                print('Script will try to create it.')
                try:
                    os.makedirs(settings['storage_path'])
                except Exception as e:
                    print(e)
                    env_errors = True
        except Exception as e:
            print('Error parsing configuration file.')
            print(e)

    # Check if all necessary commands are available
    commands = ['git', 'hg', 'svn']
    for command in commands:
        try:
            devnull = open(os.devnull)
            subprocess.Popen(
                [command],
                stdout=devnull,
                stderr=devnull
            ).communicate()
        except OSError as e:
            print('{0} command not available.'.format(command))
            env_errors = True

    if env_errors:
        print('\nPlease fix these errors and try again.')
        sys.exit(1)


def main():
    # Check environment
    settings = {}
    webstatus_path = os.path.abspath(
        os.path.join(sys.path[0], os.pardir, os.pardir))
    check_environment(webstatus_path, settings)

    storage_path = settings['storage_path']
    json_filename = os.path.join(webstatus_path, 'web', 'web_status.json')

    # Read products from external JSON file
    sources_file = open(os.path.join(
        webstatus_path, 'app', 'config', 'sources.json'))
    all_products = json.load(sources_file)
    products = {}

    # Get command line parameters
    cl_parser = argparse.ArgumentParser()
    cl_parser.add_argument('product_code', nargs='?',
                           help='Code of the single product to update')
    cl_parser.add_argument('--pretty', action='store_true',
                           help='export indented and more readable JSON')
    cl_parser.add_argument('--noupdate', action='store_true',
                           help='don\'t update local repositories (but clone them if missing)')
    args = cl_parser.parse_args()

    if (args.product_code):
        product_code = args.product_code
        if not product_code in all_products:
            print('The requested product code ({0}) is not available.'.format(
                product_code))
            sys.exit(1)
        # Use only the requested product
        products[product_code] = all_products[product_code]
        # Load the existing JSON data
        if not os.path.isfile(json_filename):
            print('{0} is not available, you need to run an update for all products first.'.format(
                json_filename))
            sys.exit(1)
        json_data = json.load(open(json_filename))
        # Remove all existing data for this product. This way, if a locale is
        # removed from the repository, we don't keep the old data.
        json_data['metadata']['products'].pop(product_code, None)
        for locale in json_data['locales']:
            json_data['locales'][locale].pop(product_code, None)
    else:
        # No product code, need to update everything and start from scratch
        products = all_products
        json_data = {}
        json_data['locales'] = {}

    # Clone/update repositories
    repository = Repositories(storage_path, args.noupdate)
    for key, product in products.iteritems():
        repository.check_repo(product)

    ignored_folders = ['.svn', '.git', '.g(config_file)it', 'dbg',
                       'db_LB', 'ja_JP_mac', 'templates',
                       'zh_Hans_CN', 'zh_Hant_TW']
    for key, product in products.iteritems():
        product_folder = os.path.join(
            storage_path,
            product['repository_name'],
            product['locale_folder']
        )

        # Reference locale could be not defined in gettext projects
        if 'reference_locale' in product:
            reference_locale = product['reference_locale']
        else:
            reference_locale = ''

        # Determine source type only once for product, create a FileAnalysis
        # object
        source_type = product.get('source_type', 'gettext')
        file_analysis = FileAnalysis(source_type, storage_path)
        file_analysis.set_reference(reference_locale)
        file_analysis.set_product_folder(product_folder)
        file_analysis.set_search_patterns(product['source_files'])

        print('\n--------\nAnalyzing: {0}'.format(product['displayed_name']))

        if os.path.isdir(product_folder):
            locales = sorted(os.listdir(product_folder))
        else:
            print('\nFolder is not available: {0}'.format(product_folder))
            locales = []

        for locale in locales:
            locale_folder = os.path.join(product_folder, locale)

            # Ignore files, consider just folders. Ignore some of them
            # based on ignored_folders and repo's excluded_folders
            if (not os.path.isdir(locale_folder)
                    or locale in ignored_folders
                    or locale in product['excluded_folders']):
                continue

            pretty_locale = locale.replace('_', '-')
            sys.stdout.write(pretty_locale + ' ')
            sys.stdout.flush()

            # Analyze files for this locale
            file_analysis.set_locale(locale)
            status_record = file_analysis.analyze_pattern()
            status_record['name'] = product['displayed_name']

            # If the pretty_locale key does not exist, I create it
            if pretty_locale not in json_data['locales']:
                json_data['locales'][pretty_locale] = {}
            json_data['locales'][pretty_locale][product['product_id']] = {}
            json_data['locales'][pretty_locale][
                product['product_id']] = status_record

    # Record some metadata, including the list of tracked products
    json_data['metadata'] = {
        'creation_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
        'products': {}
    }

    for key, product in all_products.iteritems():
        json_data['metadata']['products'][key] = {
            'name': product['displayed_name'],
            'repository_url': product['repository_url'],
            'repository_type': product['repository_type']
        }

    # Write back updated json data
    json_file = open(json_filename, 'w')
    if args.pretty:
        json_file.write(json.dumps(json_data, sort_keys=True, indent=2))
    else:
        json_file.write(json.dumps(json_data, sort_keys=True))
    json_file.close()

    print('\nAnalysis completed.')


if __name__ == '__main__':
    main()
