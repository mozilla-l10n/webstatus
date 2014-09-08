#! /usr/bin/env python

import json
import os
import subprocess
import sys
from ConfigParser import SafeConfigParser
from StringIO import StringIO
from time import strftime, localtime


def check_environment(main_path, settings):
    env_errors = False

    # Check if config file exists and parse it
    config_file = os.path.join(main_path, 'config', 'config.ini')
    if not os.path.isfile(config_file):
        print 'Configuration file (config/config.ini) is missing.'
        env_errors = True
    else:
        try:
            parser = SafeConfigParser()
            parser.readfp(open(config_file))
            settings['storage_path'] = parser.get('config', 'storage_path')
            if not os.path.isdir(settings['storage_path']):
                print 'Folder specified in config.ini is missing (%s).' % settings['storage_path']
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
                stderr = subprocess.STDOUT,
                shell = False)
            print cmd_status
        except Exception as e:
            print e
    else:
        # svn repository
        try:
            cmd_status = subprocess.check_output(
                ['svn', 'up'],
                stderr = subprocess.STDOUT,
                shell = False)
            print cmd_status
        except Exception as e:
            print e


def clone_repo(product):
    print 'Cloning repository: %s' % product['repository_url']
    if (product['repository_type'] == 'git'):
        # git repository
        try:
            cmd_status = subprocess.check_output(
                ['git', 'clone', product['repository_url']],
                stderr = subprocess.STDOUT,
                shell = False)
            print cmd_status
        except Exception as e:
            print e
    else:
        # svn repository
        try:
            cmd_status = subprocess.check_output(
                ['svn', 'co',
                 product['repository_url'], product['product_name']],
                stderr = subprocess.STDOUT,
                shell = False)
            print cmd_status
        except Exception as e:
            print e


def main():
    # Check environment
    settings = {}
    webstatus_path = os.path.join(sys.path[0], os.pardir)
    check_environment(webstatus_path, settings)

    storage_path = settings['storage_path']
    json_filename = os.path.join(webstatus_path, 'webstatus.json')
    json_data = {}

    # Read products from external Json file
    sources_file = open(os.path.join(webstatus_path, 'config', 'sources.json'))
    products = json.load(sources_file)

    # Clone/update repositories
    for key,product in products.iteritems():
        repo_path = os.path.join(storage_path, product['repository_name'])
        if os.path.isdir(repo_path):
            # Repo exists, just need to update it
            os.chdir(repo_path)
            update_repo(product)
        else:
            # Repo doesn't exist, need to clone it
            os.chdir(storage_path)
            clone_repo(product)

    ignored_folders = ['dbg', 'templates', '.svn', '.g(config_file)it']
    for key,product in products.iteritems():
        product_folder = os.path.join(
                            storage_path,
                            product['repository_name'],
                            product['locale_folder']
                         )
        for locale in sorted(os.listdir(product_folder)):
            locale_folder = os.path.join(product_folder, locale)

            # Ignore files, consider just folders. Ignore some of them
            # based on ignored_folders and repo's excluded_folders
            if (not os.path.isdir(locale_folder)
                or locale in ignored_folders
                or locale in product['excluded_folders']):
                continue

            print locale_folder
            error_status = False
            error_message = ''

            # Initialize string counts
            string_translated = 0
            string_untranslated = 0
            string_fuzzy = 0

            pretty_locale = locale.replace('_', '-')
            print 'Locale: %s' % pretty_locale

            file_path = os.path.join(locale_folder, product['po_file'])
            if os.path.isfile(file_path):
                try:
                    translation_status = subprocess.check_output(
                        ['msgfmt', '--statistics', file_path, '-o', os.devnull],
                        stderr = subprocess.STDOUT,
                        shell = False)
                    print translation_status
                except:
                    print 'Error running msgfmt on %s\n' % locale
                    error_status = True
                    string_total = 0
                    complete = False
                    error_message = 'Error extracting data with msgfmt --statistics'
            else:
                print 'File does not exist'
                error_status = True
                error_message = 'File does not exist.\n'

            if not error_status:
                po_stats_cmd = os.path.join(webstatus_path, 'script', 'postats.sh')
                string_stats_json = subprocess.check_output(
                        [po_stats_cmd, file_path],
                        stderr = subprocess.STDOUT,
                        shell = False)

                string_stats = json.load(StringIO(string_stats_json))
                string_translated = string_stats['translated']
                string_untranslated = string_stats['untranslated']
                string_fuzzy = string_stats['fuzzy']

                string_total = string_translated + string_untranslated + string_fuzzy
                if (string_untranslated == 0) & (string_fuzzy == 0):
                    # No untranslated or fuzzy strings, locale is complete
                    complete = True
                    percentage = 100
                else:
                    # Need to calculate the level of completeness
                    complete = False
                    percentage = round((float(string_translated)/string_total) * 100, 1)

            status_record = {
                'name': product['displayed_name'],
                'total': string_total,
                'untranslated': string_untranslated,
                'translated': string_translated,
                'fuzzy': string_fuzzy,
                'complete': complete,
                'percentage': percentage,
                'error_status': error_status,
                'error_message': error_message
            }

            # If the pretty_locale key does not exist, I create it
            if pretty_locale not in json_data:
                json_data[pretty_locale] = {}
            json_data[pretty_locale][product['product_name']] = {}
            json_data[pretty_locale][product['product_name']] = status_record

    # Record some metadata
    json_data['metadata'] = {
        'creation_date': strftime('%Y-%m-%d %H:%M %Z', localtime())
    }

    # Write back updated json data
    json_file = open(json_filename, 'w')
    json_file.write(json.dumps(json_data, sort_keys=True))
    json_file.close()

if __name__ == '__main__':
    main()
