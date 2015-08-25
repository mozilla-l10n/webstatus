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

$table_header = [];
foreach ($products as $code => $name) {
    array_push($table_header, $name);
}

$table_rows = [];
foreach ($locales as $locale) {
    $row = [
        'locale'   => $locale,
        'products' => [],
    ];

    $empty_product = [
        'translated'   => ' ',
        'untranslated' => ' ',
        'percentage'   => ' ',
        'style'        => '',
    ];

    foreach ($products as $code => $name) {
        $single_product = $empty_product;
        if (array_key_exists($code, $webstatus_data[$locale])) {
            $current_product = $webstatus_data[$locale][$code];
            $single_product['translated'] = $current_product['translated'];
            $single_product['untranslated'] = $current_product['untranslated'];
            $single_product['percentage'] = $current_product['percentage'];
            $single_product['style'] = Utils::getRowStyle($current_product['percentage'], 'mpstats');
        }
        array_push($row['products'], $single_product);
    }

    array_push($table_rows, $row);
}

$last_update_local = date('Y-m-d H:i e (O)', strtotime($webstatus_metadata['creation_date']));

// Add specific CSS and JS files
array_push($default_css, 'mpstats.css');
array_push($default_js, 'mpstats.js');

print $twig->render(
    'mpstats.twig',
    [
        'assets_folder'   => $assets_folder,
        'default_css'     => $default_css,
        'default_js'      => $default_js,
        'last_update'     => $last_update_local,
        'page_title'      => 'Marketplace Status',
        'products_number' => count($products),
        'table_header'    => $table_header,
        'table_rows'      => $table_rows,
    ]
);
