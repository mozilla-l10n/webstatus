Web Status
=========

This script is used to generate a Json file with the status of external Web projects based on gettext.
* webstatus.py generates the actual Json file.
* index.php can be used to view the content of the Json file (per project or per locale).

There's a running instance of both available at http://l10n.mozilla-community.org/~flod/webstatus/ (updated twice a day).

## Structure of the Json file

```JSON
locale_code: {
    product_id: {
        "complete": true/false,
        "error_message": "",
        "error_status": true/false,
        "fuzzy": number of fuzzy strings,
        "name": pretty name to display,
        "percentage": percentage of translated strings,
        "total": total number of strings,
        "translated": number of translated strings,
        "untranslated": number of untranslated strings
    }
}
```
