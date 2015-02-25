<?php
date_default_timezone_set('Europe/Rome');

$sources_file = 'config/sources.json';
$webstatus_file = 'web_status.json';

// Read the JSON files
$json_sources = json_decode(file_get_contents($sources_file), true);
$json_array = json_decode(file_get_contents($webstatus_file), true);

// Extract locales and ignore 'metadata'
$available_locales = array_keys($json_array['locales']);
sort($available_locales);

$available_products = $json_array['metadata']['products'];
// Sort elements based on 'name'
uasort($available_products, function ($a, $b) {

    return ($a < $b) ? -1 : 1;
});

// Using union to make sure "all" is the first product
$product_all = [
    'all' => [
        'name'            => 'All products',
        'repository_type' => '',
        'repository_url'  => '',
    ],
];
$available_products = $product_all + $available_products;
$xliff_note = false;

// Locale detection
if (empty($_REQUEST['locale'])) {
    // Locale was not specified, try to use locale from HTTP header
    $accept_locales = [];
    // Source: http://www.thefutureoftheweb.com/blog/use-accept-language-header
    if (isset($_SERVER['HTTP_ACCEPT_LANGUAGE'])) {
        // Break up string into pieces (languages and q factors)
        preg_match_all('/([a-z]{1,8}(-[a-z]{1,8})?)\s*(;\s*q\s*=\s*(1|0\.[0-9]+))?/i',
                       $_SERVER['HTTP_ACCEPT_LANGUAGE'],
                       $lang_parse);
        if (count($lang_parse[1])) {
            // Create a list like "en" => 0.8
            $accept_locales = array_combine($lang_parse[1], $lang_parse[4]);
            // Set default to 1 for any without q factor
            foreach ($accept_locales as $accept_locale => $val) {
                if ($val === '') {
                    $accept_locales[$accept_locale] = 1;
                }
            }
            // Sort list based on value
            arsort($accept_locales, SORT_NUMERIC);
        }
    }
    // Do I have any of these locales
    $intersection = array_values(array_intersect(array_keys($accept_locales), $available_locales));
    if (! isset($intersection[0])) {
        // This locale is not available, fall back to en-US
        $requested_locale = 'en-US';
    } else {
        $requested_locale = $intersection[0];
    }
} else {
    $requested_locale = $_REQUEST['locale'];
}

$requested_product = !empty($_REQUEST['product']) ? $_REQUEST['product'] : 'all';
// Check if the requested product is available
if (! isset($available_products[$requested_product])) {
    $requested_product = 'all';
}
if ($requested_product != 'all') {
    $requested_locale = 'all locales';
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset=utf-8>
    <title>Web Status</title>
    <link rel="stylesheet" href="assets/css/bootstrap.min.css" type="text/css" media="all" />
    <link rel="stylesheet" href="assets/css/bootstrap-theme.min.css" type="text/css" media="all" />
    <link rel="stylesheet" href="assets/css/main.css" type="text/css" media="all" />
    <link rel="stylesheet" href="assets/css/dataTables.bootstrap.css" type="text/css" media="all" />
    <script src="assets/js/jquery-1.11.2.min.js"></script>
    <script src="assets/js/jquery.dataTables.min.js"></script>
    <script src="assets/js/dataTables.bootstrap.min.js"></script>
    <script type="text/javascript">
        $(document).ready(function () {
            $('#main_table').DataTable({
                info: false,
                paging: false,
                searching: false
            });
        });
    </script>
</head>
<body>
  <div class="container">

<?php
    echo "<h1>Current locale: {$requested_locale}</h1>\n";
    echo '<div class="list locale_list">
            <p>Display localization status for a specific locale<br/>';
    foreach ($available_locales as $locale_code) {
        echo "<a href='?locale={$locale_code}'>{$locale_code}</a> ";
    }
    echo '  </p>
          </div>';

    echo "<h1>Current product: {$available_products[$requested_product]['name']}</h1>\n";
    echo '<div class="list product_list">
            <p>Display localization status for a specific project<br/>';
    foreach ($available_products as $product_code => $product) {
        echo "<a href='?product={$product_code}'>" .
             str_replace(' ', '&nbsp;', $product['name']) .
             "</a> ";
    }
    echo '  </p>
          </div>';

    $table_header = function ($row_header) {
        return '<table id="main_table" class="table table-bordered table-condensed">
            <thead>
                <tr>
                    <th>' . $row_header . '</th>
                    <th>%</th>
                    <th>Type</th>
                    <th><abbr title="Translated strings">Tran.</abbr></th>
                    <th><abbr title="Untranslated strings">Untr.</abbr></th>
                    <th><abbr title="Identical strings">Iden.</abbr></th>
                    <th><abbr title="Missing strings">Miss.</abbr></th>
                    <th>Fuzzy</th>
                    <th>Total</th>
                    <th>Errors</th>
                </tr>
            </thead>
            <tbody>';
    };

    $table_footer = '</tbody>
        </table>';

    $table_rows = function ($table_type, $row_header, $product, $source_type, $repo_url, $repo_type) {
        $perc = $product['percentage'];
        $source_type_label = $source_type;
        // For .properties files I consider also the number of identical strings
        if ($source_type == 'properties') {
            $perc_identical = $product['identical'] / $product['total'] * 100;
            if ($perc_identical > 20) {
                $perc = $perc - $perc_identical;
            }
        }

        if ($source_type == 'xliff') {
            $source_type_label = $source_type . '<a href="#xliff_notes" title="See notes"><span class="glyphicon glyphicon-info-sign" aria-hidden="true"></span></a>';
        }

        $opacity = 1;
        if ($perc < 100) {
            $opacity = floor(round(($perc - 20) / 100, 2) * 10) / 10;
        }
        if ($perc >= 70) {
            $row_style = "background-color: rgba(129, 209, 25, {$opacity})";
        } elseif ($perc >= 40) {
            $opacity = 1 - $opacity;
            $row_style = "background-color: rgba(255, 252, 61, {$opacity})";
        } else {
            $opacity = 1 - $opacity;
            $row_style = "background-color: rgba(255, 194, 115, {$opacity})";
        }

        if ($product['error_status'] == 'true') {
            $row_class = 'error';
            $row_style = '';
        } else {
            $row_class = '';
        }

        if ($table_type == 'locale') {
            $row_header = "{$row_header}<a href='{$repo_url}' class='repository_link' title='View source repository'>{$repo_type}</a>";
        }

        return  "<tr class='{$row_class}' style='{$row_style}'>\n" .
                "      <th>{$row_header}</th>\n" .
                "      <td class='number'>{$product['percentage']}</td>\n" .
                "      <td class='source_type'>{$source_type_label}</td>\n" .
                "      <td class='number'>{$product['translated']}</td>\n" .
                "      <td class='number'>{$product['untranslated']}</td>\n" .
                "      <td class='number'>{$product['identical']}</td>\n" .
                "      <td class='number'>{$product['missing']}</td>\n" .
                "      <td class='number'>{$product['fuzzy']}</td>\n" .
                "      <td class='number'>{$product['total']}</td>\n" .
                "      <td>{$product['error_message']}</td>\n" .
                "</tr>\n";
    };

    if ($requested_product == 'all') {
        // Display all products for one locale
        echo $table_header('Product');
        foreach ($available_products as $product_id => $product) {
            if (array_key_exists($product_id, $json_array['locales'][$requested_locale])) {
                $current_product = $json_array['locales'][$requested_locale][$product_id];
                if ($current_product['source_type'] == 'xliff') {
                    $xliff_note = true;
                }
                echo $table_rows('locale',
                                 $current_product['name'],
                                 $current_product,
                                 $current_product['source_type'],
                                 $product['repository_url'],
                                 $product['repository_type']);
            }
        }
        echo $table_footer;
    } else {
        // Display all locales for one product
        $completed_locales = 0;
        $total_locales = 0;
        if ($json_sources[$requested_product]['source_type'] == 'xliff') {
            $xliff_note = true;
        }
        echo $table_header('Locale');
        foreach ($available_locales as $locale_code) {
            if (isset($json_array['locales'][$locale_code][$requested_product])) {
                $current_product = $json_array['locales'][$locale_code][$requested_product];
                if ($current_product['percentage'] == 100) {
                    $completed_locales++;
                }
                $total_locales++;
                echo $table_rows('product',
                                 $locale_code,
                                 $current_product,
                                 $current_product['source_type'],
                                 '',
                                 '');
            }
        }
        echo $table_footer;
        echo "<p>Complete locales: {$completed_locales} out of {$total_locales}.</p>";
    }

    echo "<p>Last update: {$json_array['metadata']['creation_date']}</p>";

    if ($xliff_note) {
    ?>
    <h3 id="xliff_notes">Notes on XLIFF files</h3>
    <p>A MDN document is available explaining <a href="https://developer.mozilla.org/en-US/docs/Mozilla/Localization/Localizing_XLIFF_files">how to to work on XLIFF files</a>.</p>
    <ul>
        <li>Strings are reported as missing if a <code>trans-unit</code> has a <code>source</code> element but not a <code>target</code> element.</li>
        <li>Errors are reported if the XML is not valid, if there are multiple <code>source</code> or <code>target</code> elements, and if a <code>file</code> element is missing a <code>target-language</code> attribute.</li>
    </ul>
    <?php
    }
    ?>
    <p class="github_link"><a href="https://github.com/mozilla-l10n/webstatus/">Code hosted on GitHub</a></p>
  </div>
</body>
</html>
