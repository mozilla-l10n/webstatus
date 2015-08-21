<?php
namespace Webstatus;

require __DIR__ . '/app/inc/init.php';

$webstatus = new Webstatus($webstatus_file, $sources_file);
$available_locales = $webstatus->getAvailableLocales();
$available_products =  $webstatus->getAvailableProducts();
$webstatus_data = $webstatus->getWebstatusData();
$webstatus_metadata = $webstatus->getWebstatusMetadata();

$requested_locale = Utils::getQueryParam('locale', Utils::detectLocale($available_locales));
$requested_product = Utils::getQueryParam('product', 'all');

// Check if the requested product is supported
$supported_product = (in_array($requested_product, array_keys($available_products))) ? true : false;
if ($supported_product) {
    $product_name = $available_products[$requested_product]['name'];
} else {
    $product_name = 'N/A';
}

// Update page title
if ($requested_product != 'all') {
    $requested_locale = 'All locales';
    $page_title = "Web Status – {$product_name}";
} else {
    $page_title = "Web Status – {$requested_locale}";
}

// Determine proper URL for history page
$url_history = "https://l10n.mozilla-community.org/~flod/webstatus_history/?product={$requested_product}&";
if ($requested_locale == 'All locales') {
    $url_history .= "locale=all";
} else {
    $url_history .= "locale={$requested_locale}";
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset=utf-8>
    <title><?php echo $page_title; ?></title>
    <link rel="stylesheet" href="assets/css/bootstrap.min.css" type="text/css" media="all" />
    <link rel="stylesheet" href="assets/css/bootstrap-theme.min.css" type="text/css" media="all" />
    <link rel="stylesheet" href="assets/css/main.css" type="text/css" media="all" />
    <link rel="stylesheet" href="assets/css/dataTables.bootstrap.css" type="text/css" media="all" />
    <script src="assets/js/jquery-1.11.3.min.js"></script>
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
    <h1>
        Current locale: <?=$requested_locale?>
        <a href="<?=$url_history?>" class="stats-icon" title="See historical graphs"><span class="glyphicon glyphicon-stats" aria-hidden="true"></span></a>
    </h1>
    <div class="list locale_list">
        <p>
            Display localization status for a specific locale<br/>
<?php
    foreach ($available_locales as $locale_code) {
        echo "<a href='?locale={$locale_code}'>{$locale_code}</a> ";
    }
?>
        </p>
    </div>

    <h1>Current product: <?=$product_name?></h1>
    <div class="list product_list">
        <p>Display localization status for a specific project<br/>
<?php
    foreach ($available_products as $product_code => $product) {
        echo "<a href='?product={$product_code}'>" .
             str_replace(' ', '&nbsp;', $product['name']) .
             "</a> ";
    }
?>
        </p>
    </div>
<?php
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

    $table_rows = function ($table_type, $row_header, $product, $source_type, $repo_url, $repo_type, $product_id, $locale) {
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

        $rows =  "<tr class='{$row_class}' style='{$row_style}'>\n" .
                 "      <th>{$row_header}</th>\n" .
                 "      <td class='number'>{$product['percentage']}</td>\n" .
                 "      <td class='source_type'>{$source_type_label}</td>\n" .
                 "      <td class='number'>{$product['translated']}</td>\n";

        $link = "views/xliff_diff.php?product={$product_id}&locale={$locale}";
        if ($source_type == 'xliff' && $product['untranslated'] > 0) {
            $rows .=  "      <td class='number'><a href='{$link}' title='Show untranslated strings'>{$product['untranslated']}</a></td>\n";
        } else {
            $rows .=  "      <td class='number'>{$product['untranslated']}</td>\n";
        }

        $rows .= "      <td class='number'>{$product['identical']}</td>\n";

        if ($source_type == 'xliff' && $product['missing'] > 0) {
            $rows .=  "      <td class='number'><a href='{$link}' title='Show missing and obsolete strings'>{$product['missing']}</a></td>\n";
        } else {
            $rows .=  "      <td class='number'>{$product['missing']}</td>\n";
        }

        $rows .=  "      <td class='number'>{$product['fuzzy']}</td>\n" .
                  "      <td class='number'>{$product['total']}</td>\n" .
                  '      <td>' . htmlspecialchars($product['error_message']) . "</td>\n" .
                  "</tr>\n";

        return $rows;
    };

    if ($requested_product == 'all') {
        if (! in_array($requested_locale, $available_locales)) {
            echo '<h1>Unsupported locale</h1><p>The requested locale is not supported.</p>';
        } else {
            // Display all products for one locale
            echo $table_header('Product');
            foreach ($available_products as $product_id => $product) {
                if (array_key_exists($product_id, $webstatus_data[$requested_locale])) {
                    $current_product = $webstatus_data[$requested_locale][$product_id];
                    $xliff_note = ($current_product['source_type'] == 'xliff') ? true : false;
                    echo $table_rows('locale',
                                     $current_product['name'],
                                     $current_product,
                                     $current_product['source_type'],
                                     $product['repository_url'],
                                     $product['repository_type'],
                                     $product_id,
                                     $requested_locale);
                }
            }
            echo $table_footer;
        }
    } else {
        // Display all locales for one product
        $completed_locales = 0;
        $total_locales = 0;

        if (! $supported_product) {
            echo '<h1>Unsupported product</h1><p>The requested product is not supported.</p>';
        } else {
            $xliff_note = ($webstatus->getSourceType($requested_product) == 'xliff') ? true : false;
            echo $table_header('Locale');
            foreach ($available_locales as $locale_code) {
                if (isset($webstatus_data[$locale_code][$requested_product])) {
                    $current_product = $webstatus_data[$locale_code][$requested_product];
                    if ($current_product['percentage'] == 100) {
                        $completed_locales++;
                    }
                    $total_locales++;
                    echo $table_rows('product',
                                     $locale_code,
                                     $current_product,
                                     $current_product['source_type'],
                                     '',
                                     '',
                                     $requested_product,
                                     $locale_code);
                }
            }
            echo $table_footer;
            echo "<p>Complete locales: {$completed_locales} out of {$total_locales}.</p>";
        }
    }

    $last_update_local = date('Y-m-d H:i e (O)', strtotime($webstatus_metadata['creation_date']));
    echo "<p>Last update: {$last_update_local}</p>";

    if (isset($xliff_note) && $xliff_note) {
        ?>
    <h3 id="xliff_notes">Notes on XLIFF files</h3>
    <p>A MDN document is available explaining
       <a href="https://developer.mozilla.org/en-US/docs/Mozilla/Localization/Localizing_XLIFF_files">how to to work on XLIFF files</a>.</p>
    <ul>
        <li>Strings are reported as missing if a <code>trans-unit</code> has a <code>source</code> element
            but not a <code>target</code> element.</li>
        <li>Don't use straight double quotes (<code>"example"</code>) in your translations. Use curly double
            quotes (<code>“example”</code>) or straight single quotes (<code>'example'</code>).</li>
        <li>Errors are reported if the XML is not valid, if there are multiple <code>source</code> or
            <code>target</code> elements, and if the first <code>file</code> element is missing a
            <code>target-language</code> attribute.</li>
        <li>Untranslated strings are strings available in the file but not localized (no <code>target</code>).
        Missing strings are strings available in en-US but not in the locale file. Completion percentage is
        determined by adding the number of missing strings to the number of strings actually available in the file.</li>
    </ul>
    <?php

    }
    ?>
    <p class="github_link"><a href="https://github.com/mozilla-l10n/webstatus/">Code hosted on GitHub</a></p>
  </div>
</body>
</html>
