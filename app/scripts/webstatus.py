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


def analyze_gettext(locale, product_folder, source_files, script_path, string_count, error_record):
    # Analyze gettext (po) files

    # Get a list of all files in the locale folder, I don't use a
    # reference file for gettext
    locale_files = []
    for source_file in source_files:
        locale_files += glob.glob(os.path.join(product_folder,
                                               locale, source_file))
    locale_files.sort()

    errors = False
    for locale_file in locale_files:
        # Check if msgfmt returns errors
        try:
            translation_status = subprocess.check_output(
                ['msgfmt', '--statistics', locale_file,
                 '-o', os.devnull],
                stderr=subprocess.STDOUT,
                shell=False)
        except:
            print 'Error running msgfmt on %s\n' % locale
            errors = True
            error_record[
                'message'] = 'Error extracting data with msgfmt --statistics'

        if not errors:
            try:
                po_stats_cmd = os.path.join(script_path, 'postats.sh')
                string_stats_json = subprocess.check_output(
                    [po_stats_cmd, locale_file],
                    stderr=subprocess.STDOUT,
                    shell=False)
                script_output = json.load(StringIO(string_stats_json))
                string_count['fuzzy'] += script_output['fuzzy']
                string_count['translated'] += script_output['translated']
                string_count['untranslated'] += script_output['untranslated']
                string_count['total'] += script_output['total']
            except Exception as e:
                print e
                errors = True
                error_record['message'] = 'Error extracting stats'

    if errors:
        error_record['status'] = True
        complete = False


def analyze_properties(locale, reference_locale, product_folder, source_files, script_path, string_count, error_record):
    # Analyze properties files

    errors = False
    for source_file in source_files:
        # source_file can include wildcards, e.g. *.properties
        # properties_stats.py supports wildcards, no need to pass one file
        # at the time.
        try:
            try:
                compare_script = os.path.join(
                    script_path, 'properties_stats.py')
                string_stats_json = subprocess.check_output(
                    [compare_script, product_folder,
                     source_file, reference_locale, locale],
                    stderr=subprocess.STDOUT,
                    shell=False)
            except subprocess.CalledProcessError as error:
                errors = True
                error_record['message'] = 'Error extracting data: %s' % str(
                    error.output)
            except:
                errors = True
                error_record['message'] = 'Error extracting data'

            script_output = json.load(StringIO(string_stats_json))
            for file_name, file_data in script_output.iteritems():
                string_count['identical'] += file_data['identical']
                string_count['missing'] += file_data['missing']
                string_count['translated'] += file_data['translated']
                string_count['total'] += file_data['total']

        except Exception as e:
            print e
            errors = True
            error_record['message'] = 'Error extracting stats'

    if errors:
        error_record['status'] = True
        complete = False


def analyze_xliff(locale, reference_locale, product_folder, source_files, script_path, string_count, error_record):
    # Analyze XLIFF files

    errors = False
    for source_file in source_files:
        # source_file can include wildcards, e.g. *.xliff
        # xliff_stats.py supports wildcards, no need to pass one file
        # at the time.
        try:
            try:
                compare_script = os.path.join(script_path, 'xliff_stats.py')
                string_stats_json = subprocess.check_output(
                    [compare_script, product_folder,
                     source_file, reference_locale, locale],
                    stderr=subprocess.STDOUT,
                    shell=False)
            except subprocess.CalledProcessError as error:
                errors = True
                error_record['message'] = 'Error extracting data: %s' % str(
                    error.output)
            except:
                errors = True
                error_record['message'] = 'Error extracting data'

            script_output = json.load(StringIO(string_stats_json))
            for file_name, file_data in script_output.iteritems():
                string_count['identical'] += file_data['identical']
                string_count['missing'] += file_data['missing']
                string_count['translated'] += file_data['translated']
                string_count['untranslated'] += file_data['untranslated']
                string_count['total'] += file_data['total']
                if file_data['errors'] != '':
                    # For XLIFF I might have errors but still display
                    # the available stats
                    errors = True
                    error_record['message'] = 'Error extracting data: %s' % \
                        file_data['errors']
        except Exception as e:
            print e
            errors = True
            error_record['message'] = 'Error extracting stats'

    if errors:
        error_record['status'] = True
        complete = False


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
            print "The requested product code (%s) is not available." \
                  % product_code
            sys.exit(1)
        # Use only the requested product
        products[product_code] = all_products[product_code]
        # Load the existing JSON data
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

        # Reference locale is not defined in gettext projects
        if 'reference_locale' in product:
            reference_locale = product['reference_locale']
        else:
            reference_locale = ''

        print "\n--------\nAnalyzing: %s" % product['displayed_name']

        for locale in sorted(os.listdir(product_folder)):
            locale_folder = os.path.join(product_folder, locale)

            # Ignore files, consider just folders. Ignore some of them
            # based on ignored_folders and repo's excluded_folders
            if (not os.path.isdir(locale_folder)
                    or locale in ignored_folders
                    or locale in product['excluded_folders']):
                continue

            pretty_locale = locale.replace('_', '-')
            print pretty_locale,

            if 'source_type' in product:
                source_type = product['source_type']
            else:
                source_type = 'gettext'

            error_record = {
                'status': False,
                'message': ''
            }

            # Initialize string counters
            string_count = {
                'fuzzy': 0,
                'identical': 0,
                'missing': 0,
                'translated': 0,
                'untranslated': 0,
                'total': 0
            }
            percentage = 0

            # Analyze file
            if source_type == 'xliff':
                analyze_xliff(
                    locale, reference_locale,
                    product_folder, product['source_files'], script_path,
                    string_count, error_record
                )
            elif source_type == 'properties':
                analyze_properties(
                    locale, reference_locale,
                    product_folder, product['source_files'], script_path,
                    string_count, error_record
                )
            elif source_type == 'gettext':
                analyze_gettext(
                    locale,
                    product_folder, product['source_files'], script_path,
                    string_count, error_record
                )

            # Calculate stats
            if (string_count['total'] == 0 and
                    not error_record['status']):
                # This locale has 0 strings (it might happen for a project with
                # .properties files and an empty folder)
                complete = False
                percentage = 0
            elif (string_count['fuzzy'] == 0 and
                    string_count['missing'] == 0 and
                    string_count['untranslated'] == 0):
                # No untranslated, missing or fuzzy strings, locale is
                # complete
                complete = True
                percentage = 100
            elif (string_count['missing'] > 0):
                complete = False
                percentage = round(
                    (float(string_count['translated']) / (string_count['total'] + string_count['missing'])) * 100, 1)
            else:
                # Need to calculate the level of completeness
                complete = False
                percentage = round(
                    (float(string_count['translated']) / string_count['total']) * 100, 1)

            status_record = {
                'complete': complete,
                'error_message': error_record['message'],
                'error_status': error_record['status'],
                'fuzzy': string_count['fuzzy'],
                'identical': string_count['identical'],
                'missing': string_count['missing'],
                'name': product['displayed_name'],
                'percentage': percentage,
                'total': string_count['total'],
                'translated': string_count['translated'],
                'source_type': source_type,
                'untranslated': string_count['untranslated']
            }

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
