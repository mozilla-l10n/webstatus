Web Status
=========

Python script and PHP Web views used to analyze Web projects based on Gettext (.po) files.
* ```script/webstatus.py``` generates a JSON file for all listed projects.
* ```index.php``` is used to display the content of the JSON file, per project or per locale.
* ```mpstats/index.php``` is used to display projects related to Marketplace for all locales in a single page.

Prerequisites:
* Copy ```config/config.ini-dist``` as ```config/config.ini```, adapting the path to your system. This is the path used to store all local clones (currently about 1 GB of space required).
* You need ```git```, ```svn``` and ```msgfmt```(included in package *gettext*) on your system.

## Available URLS
```
/
```
Main Web Status view.

```
/mpstats
```
Marketplace Stats view.

See a running instance at http://l10n.mozilla-community.org/~flod/webstatus/

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
        "product_name": webproject_id,
        "repository_name": name of the local folder used to store the clone,
        "repository_type": type of repository (svn, git),
        "repository_url": URL of the repository,
        "source_file": file name (typically 'LC_MESSAGES/messages.po'),
        "source_type": source type (gettext, properties, xliff)
    },
```
