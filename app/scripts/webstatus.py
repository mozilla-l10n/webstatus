#! /usr/bin/env python

import argparse
import json
import os
import subprocess
import sys
from ConfigParser import SafeConfigParser
from StringIO import StringIO
from datetime import datetime


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


def clone_repo(product):
    print 'Cloning repository: %s' % product['repository_url']
    if (product['repository_type'] == 'git'):
        # git repository
        try:
            cmd_status = subprocess.check_output(
                ['git', 'clone', '--depth', '1', product['repository_url']],
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
                 product['repository_url'], product['product_name']],
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
    check_environment(webstatus_path, settings)

    storage_path = settings['storage_path']
    json_filename = os.path.join(webstatus_path, 'web', 'web_status.json')

    # Read products from external Json file
    sources_file = open(os.path.join(
        webstatus_path, 'app', 'config', 'sources.json'))
    all_products = json.load(sources_file)
    products = {}

    # Get command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('product_code', nargs='?',
                        help='Code of the single product to update')
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
        repo_path = os.path.join(storage_path, product['repository_name'])
        if os.path.isdir(repo_path):
            # Repo exists, just need to update it
            os.chdir(repo_path)
            update_repo(product)
        else:
            # Repo doesn't exist, need to clone it
            os.chdir(storage_path)
            clone_repo(product)

    ignored_folders = ['.svn', '.git', '.g(config_file)it', 'dbg',
                       'db_LB', 'ja_JP_mac', 'templates',
                       'zh_Hans_CN', 'zh_Hant_TW']
    for key, product in products.iteritems():
        product_folder = os.path.join(
            storage_path,
            product['repository_name'],
            product['locale_folder']
        )

        if product['underscore_locales']:
            reference_locale = 'en_US'
        else:
            reference_locale = 'en-US'

        for locale in sorted(os.listdir(product_folder)):
            locale_folder = os.path.join(product_folder, locale)

            # Ignore files, consider just folders. Ignore some of them
            # based on ignored_folders and repo's excluded_folders
            if (not os.path.isdir(locale_folder)
                    or locale in ignored_folders
                    or locale in product['excluded_folders']):
                continue

            print locale_folder
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

            pretty_locale = locale.replace('_', '-')
            print 'Locale: %s' % pretty_locale

            if 'source_type' in product:
                source_type = product['source_type']
            else:
                source_type = 'gettext'

            for source_file in product['source_files']:
                locale_file_name = os.path.join(locale_folder, source_file)
                if os.path.isfile(locale_file_name):
                    missing_file = False
                    # Gettext files: check if msgfmt returns errors
                    if source_type == 'gettext':
                        try:
                            translation_status = subprocess.check_output(
                                ['msgfmt', '--statistics', locale_file_name,
                                 '-o', os.devnull],
                                stderr=subprocess.STDOUT,
                                shell=False)
                            print translation_status
                        except:
                            print 'Error running msgfmt on %s\n' % locale
                            error_record['status'] = True
                            string_count['total'] = 0
                            complete = False
                            error_record[
                                'message'] = 'Error extracting data with msgfmt --statistics'
                else:
                    missing_file = True
                    if not source_type == 'properties':
                        # I want to stop for all source types except properties
                        print 'File does not exist'
                        error_record['status'] = True
                        error_record['message'] = 'File does not exist.\n'

                if not error_record['status']:
                    try:
                        # Gettext files
                        if source_type == 'gettext':
                            po_stats_cmd = os.path.join(
                                webstatus_path, 'app', 'scripts', 'postats.sh')
                            string_stats_json = subprocess.check_output(
                                [po_stats_cmd, locale_file_name],
                                stderr=subprocess.STDOUT,
                                shell=False)
                            string_stats = json.load(
                                StringIO(string_stats_json))
                            string_count['fuzzy'] += string_stats['fuzzy']
                            string_count[
                                'translated'] += string_stats['translated']
                            string_count[
                                'untranslated'] += string_stats['untranslated']
                            string_count['total'] += string_stats['total']

                        # Properties files
                        if source_type == 'properties':
                            try:
                                compare_script = os.path.join(
                                    webstatus_path, 'app',
                                    'scripts', 'properties_compare.py')
                                source_file_name = os.path.join(
                                    product_folder, reference_locale, source_file)
                                # If the localized file is missing, compare
                                # source against itself
                                if missing_file:
                                    locale_file_name = source_file_name
                                string_stats_json = subprocess.check_output(
                                    [compare_script,
                                     source_file_name,
                                     locale_file_name
                                     ],
                                    stderr=subprocess.STDOUT,
                                    shell=False)
                            except subprocess.CalledProcessError as error:
                                error_record['status'] = True
                                string_count['total'] = 0
                                complete = False
                                error_record['message'] = 'Error extracting data: %s' % str(
                                    error.output)
                            except:
                                error_record['status'] = True
                                string_count['total'] = 0
                                complete = False
                                error_record[
                                    'message'] = 'Error extracting data'

                            string_stats = json.load(
                                StringIO(string_stats_json))
                            if not missing_file:
                                string_count[
                                    'identical'] += string_stats['identical']
                                string_count[
                                    'missing'] += string_stats['missing']
                                string_count[
                                    'translated'] += string_stats['translated']
                                string_count['total'] += string_stats['total']
                            else:
                                # File is missing, count all the strings as
                                # missing
                                string_count[
                                    'missing'] += string_stats['total']
                                string_count['total'] += string_stats['total']

                        # Xliff files
                        if source_type == 'xliff':
                            try:
                                compare_script = os.path.join(
                                    webstatus_path, 'app',
                                    'scripts', 'xliff_stats.py')
                                reference_file_name = os.path.join(
                                    product_folder, reference_locale, source_file)
                                string_stats_json = subprocess.check_output(
                                    [compare_script, reference_file_name,
                                     locale_file_name],
                                    stderr=subprocess.STDOUT,
                                    shell=False)
                            except subprocess.CalledProcessError as error:
                                error_record['status'] = True
                                string_count['total'] = 0
                                complete = False
                                error_record['message'] = 'Error extracting data: %s' % str(
                                    error.output)
                            except:
                                error_record['status'] = True
                                string_count['total'] = 0
                                complete = False
                                error_record[
                                    'message'] = 'Error extracting data'
                            string_stats = json.load(
                                StringIO(string_stats_json))
                            string_count[
                                'identical'] += string_stats['identical']
                            string_count['missing'] += string_stats['missing']
                            string_count[
                                'translated'] += string_stats['translated']
                            string_count[
                                'untranslated'] += string_stats['untranslated']
                            string_count['total'] += string_stats['total']
                            if string_stats['errors'] != '':
                                # For XLIFF I might have errors but still display
                                # the available stats
                                error_record['status'] = True
                                complete = False
                                error_record['message'] = 'Error extracting data: %s' % \
                                    string_stats['errors']
                    except Exception as e:
                        print e
                        error_record['status'] = True
                        string_count['total'] = 0
                        complete = False
                        error_record['message'] = 'Error extracting stats'

            # Run stats
            if (string_count['fuzzy'] == 0 and
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
            json_data['locales'][pretty_locale][product['product_name']] = {}
            json_data['locales'][pretty_locale][
                product['product_name']] = status_record

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
    json_file.write(json.dumps(json_data, sort_keys=True))
    json_file.close()

if __name__ == '__main__':
    main()
