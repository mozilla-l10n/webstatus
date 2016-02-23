<?php
namespace Webstatus;

$products = [
    'fireplace'         => '',
    'spartacus'         => '',
    'zippy'             => '',
    'zamboni'           => '',
    'marketplace-stats' => '',
    'commbadge'         => '',
];

$excluded_locales = [
    'ach', 'ak', 'an', 'az', 'br', 'cak', 'db-LB', 'en', 'en-GB',
    'en-US', 'en-ZA', 'es-AR', 'es-CL', 'es-ES', 'es-MX', 'fur',
    'fy', 'fy-NL', 'ga', 'gu-IN', 'hi', 'hy-AM', 'is', 'ka', 'kk',
    'lo', 'lv', 'mai', 'metadata', 'ml-IN', 'mr', 'nb', 'nn-NO',
    'no', 'nso', 'oc', 'pa-IN', 'pt', 'rm', 'rw', 'sah', 'son',
    'sr-Cyrl', 'sr-CYRL', 'sr-LATN', 'sv', 'ta-LK', 'tsz', 'uz',
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

print $twig->render(
    'mpstats.twig',
    [
        'page_title'      => 'Marketplace Status',
        'products_number' => count($products),
        'table_header'    => $table_header,
        'table_rows'      => $table_rows,
    ]
);
