<?php
namespace Webstatus;

$webstatus = new Webstatus($webstatus_file, $sources_file);
$available_locales = $webstatus->getAvailableLocales();
$available_products =  $webstatus->getAvailableProducts();
$webstatus_data = $webstatus->getWebstatusData();
$webstatus_metadata = $webstatus->getWebstatusMetadata();

$products = [
    'fireplace'         => '',
    'spartacus'         => '',
    'zippy'             => '',
    'zamboni'           => '',
    'marketplace-stats' => '',
    'commbadge'         => '',
];

$excluded_locales = [
    'ak', 'an', 'az', 'br', 'db-LB', 'en', 'en-GB', 'en-US', 'en-ZA',
    'es-AR', 'es-CL', 'es-ES', 'es-MX', 'fur', 'fy', 'fy-NL', 'ga', 'gu-IN',
    'hy-AM', 'is', 'kk', 'lv', 'mai', 'metadata', 'mr', 'nb', 'nn-NO',
    'no', 'oc', 'pa-IN', 'pt', 'rm', 'rw', 'sah', 'son', 'sr-Cyrl',
    'sr-CYRL', 'sr-LATN', 'sv', 'ta-LK', 'uz',
];

// Extract locales and exclude some of them
$locales = array_diff($available_locales, $excluded_locales);

// Extract product names
foreach ($webstatus_metadata['products'] as $product_id => $product) {
    if (isset($products[$product_id])) {
        $products[$product_id] = $product['name'];
    }
}

$columns_number = 1 + 3 * count($products);
