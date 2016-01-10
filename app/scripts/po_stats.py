#! /usr/bin/env python

import argparse
import json
import os

# Import Parser class
import parser


def main():
    cl_parser = argparse.ArgumentParser()
    cl_parser.add_argument('repo_folder', help='Path to repository')
    cl_parser.add_argument(
        'search_pattern', help='Search pattern for files to analyze (wildcards are supported)')
    cl_parser.add_argument('locale', help='Locale code to analyze')
    cl_parser.add_argument('--pretty', action='store_true',
                           help='export indented and more readable JSON')
    args = cl_parser.parse_args()

    file_parser = parser.GettextParser(args.repo_folder, [args.search_pattern])
    file_parser.set_locale(args.locale)
    global_stats = file_parser.analyze_files()

    if args.pretty:
        print json.dumps(global_stats, sort_keys=True, indent=2)
    else:
        print json.dumps(global_stats)


if __name__ == '__main__':
    main()
