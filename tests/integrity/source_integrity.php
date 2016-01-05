<?php
namespace Webstatus;

// Autoloading of composer dependencies
require_once __DIR__ . '/../../vendor/autoload.php';

require_once __DIR__ . '/../../app/inc/init.php';

$sources_json_data = json_decode(file_get_contents($sources_file), true);

// Check if product_id matches the repository ID
foreach ($sources_json_data as $product_id => $product_data) {
    if ($product_id != $product_data['product_id']) {
        $errors[] = "product_id for '{$product_id}' has to match '{$product_data['product_id']}'} (found '{$product_id})' instead";
    }
}

// Check if reference_locale is defined for non gettext projects
foreach ($sources_json_data as $product_id => $product_data) {
    if ($product_data['source_type'] != 'gettext') {
        if (! isset($product_data['reference_locale'])) {
            $errors[] = "'reference_locale' is mandatory for non Gettext projects ('{$product_id}')";
        }
    }
}

if (! empty($errors)) {
    echo Utils::colorizeOutput('Detected errors during source integrity checks: ' . count($errors), 'red');
    echo implode("\n", $errors);
    echo "\n";
    exit(1);
} else {
    echo Utils::colorizeOutput('All sources look OK.', 'green');
}
