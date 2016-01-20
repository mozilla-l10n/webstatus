<?php
namespace Webstatus;

use Json\Json;

$json_object = new Json;

if ($requested_product == 'all') {
    // No product specified
    die($json_object->outputError('Product code is missing.'));
}

// Check if the requested product is available
if (! isset($available_products[$requested_product])) {
    // Product is not available
    die($json_object->outputError('Product code is not supported.'));
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
    die($json_object->outputError('Specified type is not supported. Available values: incomplete, supported.'));
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
    echo $json_object->outputContent($locales, false, true);
}
