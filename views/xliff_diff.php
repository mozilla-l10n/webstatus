<?php
date_default_timezone_set('Europe/Rome');

$html_output = '';
$error = false;

// Read locale
if (empty($_REQUEST['locale'])) {
    $html_output .= "<p>No locale requested.</p>\n";
    $error = true;
} else {
    $requested_locale = $_REQUEST['locale'];
}

// Read product, check if it uses XLIFF
$sources_file = '../config/sources.json';
$json_sources = json_decode(file_get_contents($sources_file), true);
if (! empty($_REQUEST['product'])) {
    $requested_product = $json_sources[$_REQUEST['product']];
    if ($requested_product['source_type'] != 'xliff') {
        $html_output .= "<p>This product doesn't use XLIFF files.</p>\n";
        $error = true;
    }
} else {
    $html_output .= "<p>No product requested.</p>\n";
    $error = true;
}

// Run the XLIFF compare script
$server_config = parse_ini_file(__DIR__ . '/../config/config.ini');
if (! $error) {
    if (! isset($server_config['storage_path'])) {
        $html_output = "<p>Missing or broken config/config.ini file.</p>\n";
        $error = true;
    } else {
        $base_path = $server_config['storage_path'] . DIRECTORY_SEPARATOR .
                     $requested_product['repository_name'] . DIRECTORY_SEPARATOR;
        if ($requested_product['locale_folder'] != '') {
            $base_path .= $requested_product['locale_folder'] . DIRECTORY_SEPARATOR;
        }
        $reference_file = $base_path . 'en-US' . DIRECTORY_SEPARATOR .
                          $requested_product['source_file'];
        $locale_file = $base_path .  $requested_locale . DIRECTORY_SEPARATOR .
                       $requested_product['source_file'];
        $command = "python ../script/xliff_stats.py {$reference_file} {$locale_file}";

        $json_data = json_decode(shell_exec($command), true);
    }

    $html_output .= "<h1>{$requested_product['displayed_name']} - Comparison for {$requested_locale}</h1>\n";

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
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset=utf-8>
    <title>Web Status</title>
    <link rel="stylesheet" href="../assets/css/bootstrap.min.css" type="text/css" media="all" />
    <link rel="stylesheet" href="../assets/css/bootstrap-theme.min.css" type="text/css" media="all" />
    <link rel="stylesheet" href="../assets/css/main.css" type="text/css" media="all" />
</head>
<body>
  <div class="container">
    <?php
        echo $html_output;
    ?>
  </div>
</body>
</html>
