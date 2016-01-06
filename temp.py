def analyze_gettext(locale, source_files, product_folder, script_path, string_count, error_record):
    # Analyze gettext (po) files

    # Get a list of all files in the locale folder, I don't use a
    # reference file for gettext
    locale_files = []
    print source_files
    for source_file in source_files:
        source_files += glob.glob(os.path.join(product_folder, locale, source_file))
    locale_files.sort()

    errors = False
    for locale_file_name in locale_files:
        # Check if msgfmt returns errors
        try:
            translation_status = subprocess.check_output(
                ['msgfmt', '--statistics', locale_file_name,
                 '-o', os.devnull],
                stderr=subprocess.STDOUT,
                shell=False)
        except:
            print 'Error running msgfmt on %s\n' % locale
            errors = True
            error_record[
                'message'] = 'Error extracting data with msgfmt --statistics'

        if not error_record['status']:
            try:
                po_stats_cmd = os.path.join('script_path', 'postats.sh')
                string_stats_json = subprocess.check_output(
                    [po_stats_cmd, locale_file_name],
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
