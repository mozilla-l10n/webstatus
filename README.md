Web Status
=========

Python scripts and PHP Web views used to analyze Web projects based on Gettext (.po), .properties and XLIFF files.
* ```app/scripts/webstatus.py``` generates a JSON file for all listed projects.
* ```app/scripts/webstatus.py product-id``` generates a JSON file updating only the requested ```product-id```.

Prerequisites:
* Copy ```app/config/config.ini-dist``` as ```app/config/config.ini```, adapting the variables to your system:
    * ```storage_path```is the path used to store all local clones (currently about 1 GB of space required).
    * ```web_folder``` indicates if the website is served from a root or a subfolder.
* Install [Composer](https://getcomposer.org/), a dependency manager for PHP.
* Make sure ```git```, ```hg```, ```python```, ```svn``` and ```msgfmt```(included in package *gettext*) are installed in your system.
* Run ```app/scripts/webstatus.py``` at least once to generate the data in ```/web_status.json```. If you're only interested in the front-end, you can copy an existing JSON file from a [running instance](https://l10n.mozilla-community.org/~flod/webstatus/web_status.json).

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
* ```product=XXX```: request the list of supported locales for product XXX.
* ```type=incomplete```: get only incomplete locales (missing strings or errors). Default output: all supported locales.
* ```txt```: get the response as text (default JSON).

Query example: [api/?product=firefox-ios&type=incomplete&txt](https://l10n.mozilla-community.org/~flod/webstatus/api/?product=firefox-ios&type=incomplete&txt)

A running instance of this project is available at http://l10n.mozilla-community.org/~flod/webstatus/

## Structure of the JSON file

Example at: https://l10n.mozilla-community.org/~flod/webstatus/web_status.json

```JSON
"locales": {
    "locale_code": {
        "product_id": {
            "complete": true/false,
            "error_message": "",
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
        "repository_name": name of the local folder used to store the clone,
        "repository_type": type of repository (svn, git),
        "repository_url": URL of the repository,
        "source_files": array of file names (typically 'LC_MESSAGES/messages.po'),
        "source_type": source type (gettext, properties, xliff),
        "underscore_locales": if locales use - or _ as separator (en-US vs en_US)
    },
```
