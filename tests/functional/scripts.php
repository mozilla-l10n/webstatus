<?php
define('SCRIPTS',  realpath(__DIR__ . '/../../') . '/app/scripts/');
define('TESTFILES',  realpath(__DIR__ . '/../') . '/testfiles/');

mb_internal_encoding('UTF-8');
date_default_timezone_set('Europe/Paris');

/* Compare $reference JSON with $result. Return true if identical, false
 * if they're different.
 */
function compare_json($reference, $result)
{
    $reference_array = json_decode($reference);
    $result_array = json_decode($result);

    if ($result_array != $reference_array) {
        echo "[KO] FAILED\n" .
             "Expected result:\n" .
             json_encode($reference_array, JSON_PRETTY_PRINT) .
             "\nActual result:\n" .
             json_encode($result_array, JSON_PRETTY_PRINT) . "\n";

        return false;
    }

    echo "[OK] PASSED\n";

    return true;
}

$compare_results = [];

// Test .po files
$script_name = SCRIPTS . 'postats.sh';
$target_file = TESTFILES . 'gettext/it.po';

echo "\nTesting .po file...\n";
$compare_results[] = compare_json(
    '{
        "fuzzy": 1,
        "translated": 174,
        "total": 176,
        "untranslated": 1
    }',
    shell_exec("{$script_name} {$target_file}")
);

// Test .xliff files
$script_name = SCRIPTS . 'xliff_stats.py';
$source_file = TESTFILES . 'xliff/en.xliff';
$target_file = TESTFILES . 'xliff/it.xliff';

echo "\nTesting .xliff file...\n";
$compare_results[] = compare_json(
    '{
        "identical": 0,
        "errors": "",
        "missing": 0,
        "untranslated_strings": [],
        "untranslated": 0,
        "missing_strings": [],
        "obsolete": 0,
        "translated": 6,
        "obsolete_strings": [],
        "total": 6
     }',
    shell_exec("{$script_name} {$source_file} {$target_file}")
);

$target_file = TESTFILES . 'xliff/it_errors.xliff';
$compare_results[] = compare_json(
    '{
        "identical": 0,
        "errors": "Trans unit \u201cCancel\u201d in file \u201dClient\/ClearPrivateData.strings\u201d is missing a <source> element - Trans unit \u201cClear Everything\u201d in file \u201dClient\/ClearPrivateData.strings\u201d has multiple <source> elements - Trans unit \u201cOpen in Safari\u201d in file \u201dClient\/ErrorPages.strings\u201d has multiple <target> elements - Trans unit \u201cTry again\u201d in file \u201dClient\/ErrorPages.strings\u201d has a malformed or empty <source> element",
        "missing": 0,
        "untranslated_strings": [],
        "untranslated": 0,
        "missing_strings": [],
        "obsolete": 0,
        "translated": 4,
        "obsolete_strings": [],
        "total": 4
     }',
    shell_exec("{$script_name} {$source_file} {$target_file}")
);

$target_file = TESTFILES . 'xliff/it_incomplete.xliff';
$compare_results[] = compare_json(
    '{
        "identical": 0,
        "errors": "",
        "missing": 1,
        "untranslated_strings": [
            "Client\/ClearPrivateData.strings:Cancel"
        ],
        "untranslated": 1,
        "missing_strings": [
            "Client\/ErrorPages.strings:Open in Safari"
        ],
        "obsolete": 1,
        "translated": 5,
        "obsolete_strings": [
            "Client\/ErrorPages.strings:Open in Safari1"
        ],
        "total": 6
     }',
    shell_exec("{$script_name} {$source_file} {$target_file}")
);

// Test .properties files
$script_name = SCRIPTS . 'properties_compare.py';
$source_file = TESTFILES . 'properties/en';
$target_file = TESTFILES . 'properties/fr';

echo "\nTesting .properties file...\n";
$compare_results[] = compare_json(
    '{
        "identical": 1,
        "translated": 6,
        "total": 7,
        "missing": 1
     }',
    shell_exec("{$script_name} {$source_file} {$target_file}")
);

$test_failed = 0;
foreach ($compare_results as $result) {
    if (! $result) {
        $test_failed++;
    }
}

if ($test_failed > 0) {
    echo "\nTest failures: {$test_failed}.\n";
    exit(1);
}
