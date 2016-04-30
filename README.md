# Web Status

Python scripts and PHP Web views used to analyze Web projects based on Gettext (.po), .properties and XLIFF files.
* `app/scripts/webstatus.py` generates a JSON file for all listed projects.
* `app/scripts/webstatus.py product-id` generates a JSON file updating only the requested `product-id`.

Full command line syntax:
```
usage: webstatus.py [-h] [--pretty] [--noupdate] [product_code]

positional arguments:
  product_code  Code of the single product to update

optional arguments:
  -h, --help    show this help message and exit
  --pretty      export indented and more readable JSON
  --noupdate    don't update local repositories (but clone them if missing)
```

## Installation
* Copy `app/config/config.ini-dist` as `app/config/config.ini`, adapting the variables to your system:
    * `storage_path`is the path used to store all local clones (currently about 1 GB of space required).
    * `web_folder` indicates if the website is served from a root or a subfolder.
* Install [Composer] (PHP dependency manager), either locally or globally, then install the dependencies by running `php composer.phar install` from the project's root folder.
* Make sure that `git`, `hg`, and `python` are installed in your system.
* Run `app/scripts/webstatus.py` at least once to generate the data in `/web_status.json`. If you're only interested in the front-end, you can copy an existing JSON file from a [running instance].

## Available URLS
```
/
```
Main Web Status view.

```
/mpstats
```
Marketplace Stats view.

```
/api
```
Simple API requests:
* `product=XXX`: request the list of supported locales for product XXX. Example: [Firefox for iOS supported locales].
* `type=incomplete`: get only incomplete locales (missing strings or errors). Example: [Firefox for iOS incomplete locales].
* `type=complete`: get only complete locales (no missing strings and errors). Example: [Firefox for iOS complete locales].
* `txt`: get the response as text (default JSON). Example: [Firefox for iOS supported locales in plain text format].

Without an explicit `type` output will be a list of all supported locales.

A running instance of this project is available at http://l10n.mozilla-community.org/~flod/webstatus/

## Structure of the JSON file

Example at: https://l10n.mozilla-community.org/~flod/webstatus/web_status.json

```JSON
"locales": {
    "locale_code": {
        "product_id": {
            "complete": true/false,
            "error_message": error messages (string),
            "error_status": true/false,
            "fuzzy": number of fuzzy strings,
            "identical": number of identical strings,
            "missing": number of missing strings,
            "name": pretty name to display,
            "percentage": percentage of translated strings,
            "source_type": type of source (gettext, properties),
            "total": total number of strings,
            "translated": number of translated strings,
            "untranslated": number of untranslated strings
        }
    }
}

"metadata": {
    "creation_date": creation date,
    "products": {
        "product_id": {
            "name": name of the product,
            "repository_type": type of repository (svn, git),
            "repository_url": URL of the repository
        }
    }
}
```

## Structure of the config/sources.json file

```JSON
    "webproject_id": {
        "displayed_name": displayed name,
        "excluded_folders": array of extra folders to exclude,
        "locale_folder": empty if folders for each locale are in the root of the repo
                         path if they're in a subfolder (typically 'locale'),
        "product_id": webproject_id,
        "reference_locale": locale reference code (mandatory only for .properties and XLIFF),
        "repository_name": name of the local folder used to store the clone,
        "repository_type": type of repository (svn, git),
        "repository_url": URL of the repository,
        "source_files": array of file names (typically 'LC_MESSAGES/messages.po')
                        support also wildcards (e.g. '*.properties'),
        "source_type": source type (gettext, properties, xliff)
    },
```

# License
This software is released under the terms of the [Mozilla Public License v2.0].

[Composer]: https://getcomposer.org/
[running instance]: https://l10n.mozilla-community.org/~flod/webstatus/web_status.json
[Firefox for iOS supported locales]: https://l10n.mozilla-community.org/~flod/webstatus/api/?product=firefox-ios
[Firefox for iOS incomplete locales]: https://l10n.mozilla-community.org/~flod/webstatus/api/?product=firefox-ios&type=incomplete
[Firefox for iOS complete locales]: https://l10n.mozilla-community.org/~flod/webstatus/api/?product=firefox-ios&type=complete
[Firefox for iOS supported locales in plain text format]: https://l10n.mozilla-community.org/~flod/webstatus/api/?product=firefox-ios&txt
[Mozilla Public License v2.0]: http://www.mozilla.org/MPL/2.0/
