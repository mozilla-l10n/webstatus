<?php
namespace Webstatus;

$webstatus = new Webstatus($webstatus_file, $sources_file);
$available_locales = $webstatus->getAvailableLocales();
$available_products =  $webstatus->getAvailableProducts();

$html_output = '';
$error_messages = '';

// Read locale and product
$requested_locale = Utils::getQueryParam('locale', '');
if ($requested_locale != '') {
    if (! in_array($requested_locale, $available_locales)) {
        $error_messages .= "<p>This locale is not supported.</p>\n";
    }
} else {
    $error_messages .= "<p>No locale requested.</p>\n";
}

$requested_product = Utils::getQueryParam('product', '');
if ($requested_product != '') {
    if (! isset($available_products[$requested_product])) {
        $error_messages .= "<p>This product is not supported.</p>\n";
    } elseif ($webstatus->getSourceType($requested_product) != 'xliff') {
        $error_messages .= "<p>This product doesn't use XLIFF files.</p>\n";
        $error = true;
    }
} else {
    $error_messages .= "<p>No product requested.</p>\n";
    $error = true;
}

// Run the XLIFF compare script
if ($error_messages == '') {
    $product_data = $webstatus->getSingleProductData($requested_product);
    if (! isset($server_config['storage_path'])) {
        $error_messages .= "<p>Missing or broken app/config/config.ini file.</p>\n";
    } else {
        $base_path = $server_config['storage_path'] . DIRECTORY_SEPARATOR .
                     $product_data['repository_name'] . DIRECTORY_SEPARATOR;
        if ($product_data['locale_folder'] != '') {
            $base_path .= $product_data['locale_folder'] . DIRECTORY_SEPARATOR;
        }
        $reference_file = $base_path . 'en-US' . DIRECTORY_SEPARATOR .
                          $product_data['source_file'];
        $locale_file = $base_path .  $requested_locale . DIRECTORY_SEPARATOR .
                       $product_data['source_file'];
        $script_path = __DIR__ . '/../scripts/xliff_stats.py';
        $command = "python {$script_path} {$reference_file} {$locale_file}";

        $json_data = json_decode(shell_exec($command), true);

        $html_output .= "<h1>{$product_data['displayed_name']} - Comparison for {$requested_locale}</h1>\n";

        $display_strings = function ($title, $empty_message, $string_list) {
            $local_output = '';
            if (count($string_list) == 0) {
                $local_output .= "<h2>{$title}</h2>\n<p>{$empty_message}</p>\n";
            } else {
                $local_output .= "<h2>{$title} (" . count($string_list) . ")</h2>\n<ul>\n";
                foreach ($string_list as $value) {
                    $elements = explode(':', $value);
                    $local_output .= "<li>{$elements[0]}: {$elements[1]}</li>\n";
                }
                $local_output .= "</ul>\n";
            }

            return $local_output;
        };

        $html_output .= $display_strings('Missing strings', 'No missing strings', $json_data['missing_strings']);
        $html_output .= $display_strings('Obsolete strings', 'No obsolete strings', $json_data['obsolete_strings']);
        $html_output .= $display_strings('Untranslated strings', 'No untranslated strings', $json_data['untranslated_strings']);
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset=utf-8>
    <title>Web Status</title>
    <link rel="stylesheet" href="<?=$assets_folder?>/css/bootstrap.min.css" type="text/css" media="all" />
    <link rel="stylesheet" href="<?=$assets_folder?>/css/bootstrap-theme.min.css" type="text/css" media="all" />
</head>
<body>
  <div class="container">
<?php
if ($error_messages != '') {
    echo "<h1>Error</h1>\n{$error_messages}";
} else {
    echo $html_output;
}
?>
  </div>
</body>
</html>
