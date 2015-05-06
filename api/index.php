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

$supported_locales = [];
foreach ($available_locales as $locale_code) {
    if (isset($json_webstatus['locales'][$locale_code][$requested_product])) {
        $supported_locales[] = $locale_code;
    }
}
sort($supported_locales);

if ($plain_text) {
    // TXT output
    ob_start();
    header("Content-type: text/plain; charset=UTF-8");
    foreach ($supported_locales as $locale_code) {
        echo "{$locale_code}\n";
    }
    ob_end_flush();
} else {
    // JSON output
    ob_start();
    header("access-control-allow-origin: *");
    header("Content-type: application/json; charset=UTF-8");
    echo json_encode($supported_locales, JSON_PRETTY_PRINT);
    ob_end_flush();
}
