<?php
date_default_timezone_set('Europe/Rome');

$sources_file = '../config/sources.json';
$webstatus_file = '../web_status.json';

// Read the JSON files
$json_sources = json_decode(file_get_contents($sources_file), true);
$json_webstatus = json_decode(file_get_contents($webstatus_file), true);

// Extract locales and ignore 'metadata'
$available_locales = array_keys($json_webstatus['locales']);
sort($available_locales);

$available_products = $json_webstatus['metadata']['products'];

$requested_product = !empty($_REQUEST['product']) ? $_REQUEST['product'] : '';
// Check if the requested product is available
if (! isset($available_products[$requested_product])) {
    // Product is not available
    http_response_code(400);
    die('Product code is missing or not valid.');
}

// Check if the output is JSON or plain text
$plain_text = isset($_REQUEST['txt']) ? true : false;

// Check the type of list, default 'supported' list
$list_type = isset($_REQUEST['type']) ? $_REQUEST['type'] : 'supported';

$locales = [];

if ($list_type == 'incomplete') {
    foreach ($available_locales as $locale_code) {
        if (isset($json_webstatus['locales'][$locale_code][$requested_product])) {
            if ($json_webstatus['locales'][$locale_code][$requested_product]['error_status'] ||
                $json_webstatus['locales'][$locale_code][$requested_product]['percentage'] != 100) {
                // Add locale if it has errors or it's not completely localized
                $locales[] = $locale_code;
            }
        }
    }
} elseif ($list_type == 'supported') {
    foreach ($available_locales as $locale_code) {
        if (isset($json_webstatus['locales'][$locale_code][$requested_product])) {
            $locales[] = $locale_code;
        }
    }
} else {
    http_response_code(400);
    die('Specified type is not supported. Available values: incomplete, supported.');
}

sort($locales);

if ($plain_text) {
    // TXT output
    ob_start();
    header("Content-type: text/plain; charset=UTF-8");
    foreach ($locales as $locale_code) {
        echo "{$locale_code}\n";
    }
    ob_end_flush();
} else {
    // JSON output
    ob_start();
    header("access-control-allow-origin: *");
    header("Content-type: application/json; charset=UTF-8");
    echo json_encode($locales, JSON_PRETTY_PRINT);
    ob_end_flush();
}
