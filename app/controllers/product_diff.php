<?php
namespace Webstatus;

$html_output = '';
$error_messages = '';

// Read locale and product
if ($requested_locale != '') {
    if (! in_array($requested_locale, $available_locales)) {
        $error_messages .= "<p>This locale is not supported.</p>\n";
    }
} else {
    $error_messages .= "<p>No locale requested.</p>\n";
}

if ($requested_product != '') {
    $source_type = $webstatus->getSourceType($requested_product);
    if (! isset($available_products[$requested_product])) {
        $error_messages .= "<p>This product is not supported.</p>\n";
    } elseif (! in_array($source_type, ['xliff', 'properties'])) {
        $error_messages .= "<p>This product doesn't use XLIFF or PROPERTIES files.</p>\n";
        $error = true;
    }
} else {
    $error_messages .= "<p>No product requested.</p>\n";
    $error = true;
}

// Run the specific compare script
if ($error_messages == '') {
    $product_data = $webstatus->getSingleProductData($requested_product);
    if (! isset($server_config['storage_path'])) {
        $error_messages .= "<p>Missing or broken app/config/config.ini file.</p>\n";
    } else {
        $base_path = "{$server_config['storage_path']}/{$product_data['repository_name']}/";
        if ($product_data['locale_folder'] != '') {
            $base_path .= "{$product_data['locale_folder']}/";
        }

        $display_strings = function ($title, $empty_message, $string_list) use ($source_type){
            $local_output = '';
            if (count($string_list) == 0) {
                $local_output .= "<h3>{$title}</h3>\n<p>{$empty_message}</p>\n";
            } else {
                $local_output .= "<h3>{$title} (" . count($string_list) . ")</h3>\n<ul>\n";
                foreach ($string_list as $value) {
                    $elements = explode(':', $value);
                    if ($source_type == 'xliff') {
                        $local_output .= "<li>{$elements[0]}: {$elements[1]}</li>\n";
                    } else {
                        $local_output .= "<li>{$elements[0]}</li>\n";
                    }
                }
                $local_output .= "</ul>\n";
            }

            return $local_output;
        };

        foreach ($product_data['source_files'] as $source_file) {
            /* Scripts are called xliff_stats.py, properties_stats.py and have
             * the same input parameters and output
             */
            $script_path = __DIR__ . "/../scripts/{$source_type}_stats.py";
            $command = "python {$script_path} {$base_path} {$source_file} {$product_data['reference_locale']} {$requested_locale}";

            $json_data = json_decode(shell_exec($command), true);

            foreach ($json_data as $file_name => $file_data) {
                $html_output .= "<h2>File: {$file_name}</h2>";

                $html_output .= $display_strings('Missing strings', 'No missing strings', $file_data['missing_strings']);
                $html_output .= $display_strings('Obsolete strings', 'No obsolete strings', $file_data['obsolete_strings']);
                if ($source_type == 'xliff') {
                    $html_output .= $display_strings('Untranslated strings', 'No untranslated strings', $file_data['untranslated_strings']);
                }
            }
        }
    }
}

if ($error_messages != '') {
    $content_title = "Error";
    $main_content = $error_messages;
} else {
    $content_title = "{$product_data['displayed_name']} - Comparison for {$requested_locale}";
    $main_content = $html_output;
}

print $twig->render(
    'default.twig',
    [
        'content_title' => $content_title,
        'main_content'  => $main_content,
        'page_title'    => 'Web Status - Strings Comparison',
    ]
);
