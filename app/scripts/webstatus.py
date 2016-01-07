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

# Import local files
import xliff_stats
import properties_stats


class FileAnalysis():
    '''Class used to analyze a source file pattern'''

    def __init__(self, source_type, reference_locale, product_folder, script_path):
        '''Initialize object setting parameters that remain identical across an entire product'''

        self.source_type = source_type
        self.reference_locale = reference_locale
        self.product_folder = product_folder
        self.script_path = script_path

    def analyze_pattern(self, locale, source_files):
        '''Initialize internal stats and call the specific method to perform the actual analysis'''

        # Initialize stats
        self.__initialize_stats()
        # Pick the correct analysis based on source_type
        if self.source_type == 'xliff':
            self.__analyze_xliff(locale, source_files)
        elif self.source_type == 'properties':
            self.__analyze_properties(locale, source_files)
        elif self.source_type == 'gettext':
            self.__analyze_gettext(locale, source_files)

        return self.__calculate_stats()

    def __analyze_gettext(self, locale, source_files):
        '''Analyze gettext (.po) files'''

        # Get a list of all files in the locale folder, I don't use a
        # reference file for gettext projects
        locale_files = []
        for source_file in source_files:
            locale_files += glob.glob(
                os.path.join(self.product_folder, locale, source_file))
        locale_files.sort()

        for locale_file in locale_files:
            # Check first if msgfmt returns errors
            try:
                translation_status = subprocess.check_output(
                    ['msgfmt', '--statistics', locale_file, '-o', os.devnull],
                    stderr=subprocess.STDOUT, shell=False)
            except:
                print '\nError running msgfmt on %s\n' % locale
                self.error_record[
                    'messages'] = 'Error extracting data with msgfmt'

            if not self.error_record['messages']:
                try:
                    compare_script = os.path.join(
                        self.script_path, 'postats.sh')
                    string_stats_json = subprocess.check_output(
                        [compare_script, locale_file],
                        stderr=subprocess.STDOUT, shell=False)
                    script_output = json.load(StringIO(string_stats_json))
                    self.string_count['fuzzy'] += script_output['fuzzy']
                    self.string_count[
                        'translated'] += script_output['translated']
                    self.string_count[
                        'untranslated'] += script_output['untranslated']
                    self.string_count['total'] += script_output['total']
                except Exception as e:
                    print "\n", e
                    self.error_record[
                        'messages'] = 'Error extracting stats with postats.sh'

        if self.error_record['messages']:
            self.error_record['status'] = True

    def __analyze_properties(self, locale, source_files):
        ''' Analyze properties files '''

        for source_file in source_files:
            # source_file can include wildcards, e.g. *.properties
            # properties_stats.py supports wildcards, no need to pass one file
            # at the time.
            try:
                string_stats_json = properties_stats.analyze_files(
                    self.product_folder, locale,
                    self.reference_locale, source_file
                )
                for file_name, file_data in string_stats_json.iteritems():
                    self.string_count['identical'] += file_data['identical']
                    self.string_count['missing'] += file_data['missing']
                    self.string_count['translated'] += file_data['translated']
                    self.string_count['total'] += file_data['total']
            except subprocess.CalledProcessError as e:
                print "\n", e
                self.error_record[
                    'messages'] = 'Error extracting stats: %s\n' % str(e.output)
            except Exception as e:
                print "\n", e
                self.error_record[
                    'messages'] = 'Generic error extracting stats.\n'

        if self.error_record['messages']:
            self.error_record['status'] = True

    def __analyze_xliff(self, locale, source_files):
        ''' Analyze XLIFF files '''

        for source_file in source_files:
            # source_file can include wildcards, e.g. *.xliff
            # xliff_stats.py supports wildcards, no need to pass one file
            # at the time.
            try:
                string_stats_json = xliff_stats.analyze_files(
                    self.product_folder, locale,
                    self.reference_locale, source_file
                )
                for file_name, file_data in string_stats_json.iteritems():
                    self.string_count['identical'] += file_data['identical']
                    self.string_count['missing'] += file_data['missing']
                    self.string_count['translated'] += file_data['translated']
                    self.string_count[
                        'untranslated'] += file_data['untranslated']
                    self.string_count['total'] += file_data['total']
                    if file_data['errors'] != '':
                        self.error_record[
                            'messages'] = 'Error extracting stats: %s\n' % file_data['errors']
            except Exception as e:
                print "\n", e
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


def check_environment(main_path, settings):
    env_errors = False

    # Check if config file exists and parse it
    config_file = os.path.join(main_path, 'app', 'config', 'config.ini')
    if not os.path.isfile(config_file):
        print 'Configuration file (app/config/config.ini) is missing.'
        env_errors = True
    else:
        try:
            parser = SafeConfigParser()
            parser.readfp(open(config_file))
            settings['storage_path'] = parser.get('config', 'storage_path')
            if not os.path.isdir(settings['storage_path']):
                print 'Folder specified in config.ini is missing (%s).' \
                    % settings['storage_path']
                print 'Script will try to create it.'
                try:
                    os.makedirs(settings['storage_path'])
                except Exception as e:
                    print e
                    env_errors = True
        except Exception as e:
            print 'Error parsing configuration file.'
            print e

    # Check if all necessary commands are available
    commands = ['msgfmt', 'git', 'svn']
    for command in commands:
        try:
            devnull = open(os.devnull)
            subprocess.Popen(
                [command],
                stdout=devnull,
                stderr=devnull
            ).communicate()
        except OSError as e:
            print '%s command not available.' % command
            env_errors = True

    if env_errors:
        print '\nPlease fix these errors and try again.'
        sys.exit(0)


def check_repo(storage_path, product, noupdate):
    repo_path = os.path.join(storage_path, product['repository_name'])
    if os.path.isdir(repo_path):
        # Folder exists, check if it's actually a repository
        if os.path.isdir(os.path.join(repo_path, '.' + product['repository_type'])):
            # Update existing repository if needed
            if not noupdate:
                os.chdir(repo_path)
                update_repo(product)
        else:
            # Delete folder and re-clone
            print 'Removing folder (not a valid repository): %s' % repo_path
            shutil.rmtree(repo_path)
            os.chdir(storage_path)
            clone_repo(product)
    else:
        # Repository doesn't exist, need to clone it
        os.chdir(storage_path)
        clone_repo(product)


def clone_repo(product):
    print 'Cloning repository: %s' % product['repository_url']
    if (product['repository_type'] == 'git'):
        # git repository
        try:
            cmd_status = subprocess.check_output(
                ['git', 'clone', '--depth', '1',
                 product['repository_url'], product['repository_name']],
                stderr=subprocess.STDOUT,
                shell=False)
            print cmd_status
        except Exception as e:
            print e
    else:
        # svn repository
        try:
            cmd_status = subprocess.check_output(
                ['svn', 'co',
                 product['repository_url'], product['repository_name']],
                stderr=subprocess.STDOUT,
                shell=False)
            print cmd_status
        except Exception as e:
            print e


def update_repo(product):
    print 'Updating repository: %s' % product['displayed_name']
    if (product['repository_type'] == 'git'):
        # git repository
        try:
            cmd_status = subprocess.check_output(
                ['git', 'pull'],
                stderr=subprocess.STDOUT,
                shell=False)
            print cmd_status
        except Exception as e:
            print e
    else:
        # svn repository
        try:
            cmd_status = subprocess.check_output(
                ['svn', 'up'],
                stderr=subprocess.STDOUT,
                shell=False)
            print cmd_status
        except Exception as e:
            print e


def main():
    # Check environment
    settings = {}
    webstatus_path = os.path.abspath(
        os.path.join(sys.path[0], os.pardir, os.pardir))
    script_path = os.path.join(webstatus_path, 'app', 'scripts')
    check_environment(webstatus_path, settings)

    storage_path = settings['storage_path']
    json_filename = os.path.join(webstatus_path, 'web', 'web_status.json')

    # Read products from external JSON file
    sources_file = open(os.path.join(
        webstatus_path, 'app', 'config', 'sources.json'))
    all_products = json.load(sources_file)
    products = {}

    # Get command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('product_code', nargs='?',
                        help='Code of the single product to update')
    parser.add_argument('--pretty', action='store_true',
                        help='export indented and more readable JSON')
    parser.add_argument('--noupdate', action='store_true',
                        help='don\'t update local repositories (but clone them if missing)')
    args = parser.parse_args()

    if (args.product_code):
        product_code = args.product_code
        if not product_code in all_products:
            print 'The requested product code (%s) is not available.' \
                  % product_code
            sys.exit(1)
        # Use only the requested product
        products[product_code] = all_products[product_code]
        # Load the existing JSON data
        if not os.path.isfile(json_filename):
            print '%s is not available, you need to run an update for all products first.' % json_filename
            sys.exit(1)
        json_data = json.load(open(json_filename))
    else:
        # No product code, need to update everything and start from scratch
        products = all_products
        json_data = {}
        json_data['locales'] = {}

    # Clone/update repositories
    for key, product in products.iteritems():
        check_repo(storage_path, product, args.noupdate)

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
        file_analysis = FileAnalysis(
            source_type, reference_locale, product_folder, script_path)

        print '\n--------\nAnalyzing: %s' % product['displayed_name']
        for locale in sorted(os.listdir(product_folder)):
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

            # Analyze file
            status_record = file_analysis.analyze_pattern(
                locale, product['source_files'])
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

if __name__ == '__main__':
    main()
