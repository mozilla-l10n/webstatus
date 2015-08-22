<?php
namespace Webstatus;

$webstatus = new Webstatus($webstatus_file, $sources_file);
$available_locales = $webstatus->getAvailableLocales();
$available_products =  $webstatus->getAvailableProducts();
$webstatus_data = $webstatus->getWebstatusData();

// Check if the requested product is available
$requested_product = Utils::getQueryParam('product', '');
if (! isset($available_products[$requested_product])) {
    // Product is not available
    http_response_code(400);
    die('Product code is missing or not valid.');
}

// Check if the output is JSON or plain text
$plain_text = Utils::getQueryParam('txt', false);

// Check the type of list, default 'supported' list
$list_type = Utils::getQueryParam('type', 'supported');

$locales = [];
if ($list_type == 'incomplete') {
    foreach ($available_locales as $locale_code) {
        if (isset($webstatus_data[$locale_code][$requested_product])) {
            if ($webstatus_data[$locale_code][$requested_product]['error_status'] ||
                $webstatus_data[$locale_code][$requested_product]['percentage'] != 100) {
                // Add locale if it has errors or it's not completely localized
                $locales[] = $locale_code;
            }
        }
    }
} elseif ($list_type == 'supported') {
    foreach ($available_locales as $locale_code) {
        if (isset($webstatus_data[$locale_code][$requested_product])) {
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
