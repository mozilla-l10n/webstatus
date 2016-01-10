#! /usr/bin/env python

import glob
import os


def list_diff(a, b):
    ''' Return list of elements of list a not available in list b '''
    b = set(b)
    return [aa for aa in a if aa not in b]


def create_file_list(repo_folder, locale, pattern):
    ''' Search all files to analyze '''

    # Get a list of all files to analyze, since source_pattern can use
    # wildcards
    locale_files = glob.glob(
        os.path.join(repo_folder, locale, pattern)
    )
    locale_files.sort()

    return locale_files
