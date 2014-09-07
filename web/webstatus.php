<?php

function getRowStyle($current_product) {
    $perc = $current_product['percentage'];
    $opacity = 1;
    if ($perc < 100) {
        $opacity = floor(round(($perc-20)/100,2)*10)/10;
    }
    if ($perc >= 70) {
        $stylerow = "background-color: rgba(129, 209, 25, {$opacity})";
    } elseif ($perc >= 40) {
        $opacity = 1 - $opacity;
        $stylerow = "background-color: rgba(255, 252, 61, {$opacity})";
    } else {
        $opacity = 1 - $opacity;
        $stylerow = "background-color: rgba(255, 174, 61, {$opacity})";
    }

    if ($current_product['error_status'] == 'true') {
        $classrow = 'error';
        $stylerow = '';
    } else {
        $classrow = '';
    }

    return [
        'class' => $classrow,
        'style' => $stylerow,
    ];
}

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset=utf-8>
    <title>Web Status</title>
    <link rel="stylesheet" href="css/webstatus.css" type="text/css" media="all" />
</head>

<body>

<?php
    date_default_timezone_set('Europe/Rome');
    $file_name = '../webstatus.json';
    $file_cache = 'cache/details.inc';

    // Read the json file
    $json_array = (array) json_decode(file_get_contents($file_name), true);

    // Check how old the cache files are for products and locales
    if ((! file_exists($file_cache)) || (time() - filemtime($file_cache) >= 60*60)) {
        // File is older than 1 hour or doesn't exist, regenerate arrays and save it
        $available_locales = [];
        $ignored_locales = ['ja-JP-mac', 'metadata', 'zh-Hant-TW'];
        foreach (array_keys($json_array) as $locale_code) {
            if (! in_array($locale_code, $ignored_locales)) {
                $available_locales[$locale_code] = $locale_code;
            }
        }

        $available_products = [];
        $available_products['all'] = ' all products';
        foreach ($available_locales as $locale_code) {
            foreach (array_keys($json_array[$locale_code]) as $product_code) {
                if (! in_array($product_code, $available_products)) {
                    $available_products[$product_code] = $json_array[$locale_code][$product_code]['name'];
                }
            }
        }
        asort($available_products);
        $file_content = '<?php' . PHP_EOL;
        $file_content .= '$available_locales = ' . var_export($available_locales, true) . ';' . PHP_EOL;
        $file_content .= '$available_products = ' . var_export($available_products, true) . ';' . PHP_EOL;
        file_put_contents($file_cache, $file_content);
    } else {
        // File is recent, no need to regenerate the arrays
        include_once $file_cache;
        echo '<!-- Using cached file: ' . date ('Y-m-d H:i', filemtime($file_cache)) . "-->\n";
    }

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

    if ($requested_product != 'all') {
        $requested_locale = 'all locales';
    }

    echo '<h1>Current locale: ' . $requested_locale . "</h1>\n";
    echo '<div class="list">
            <p>Display localization status for a specific locale<br/>';
    foreach ($available_locales as $locale_code) {
        echo '<a href="?locale=' . $locale_code . '">' . $locale_code . '</a>&nbsp; ';
    }
    echo "  </p>
          </div>";

    echo '<h1>Current product: ' . $available_products[$requested_product] . "</h1>\n";
    echo '<div class="list">
            <p>Display localization status for a specific project<br/>';
    foreach ($available_products as $product_code => $product_name) {
        echo '<a href="?product=' . $product_code . '">' . $product_name . '</a>&nbsp; ';
    }
    echo '  </p>
          </div>';

    if ($requested_product == 'all') {
        // Display all products for one locale
        ?>
        <table>
            <thead>
                <tr>
                    <th>Product</th>
                    <th>%</th>
                    <th>Translated</th>
                    <th>Untransl.</th>
                    <th>Fuzzy</th>
                    <th>Total</th>
                    <th>Errors</th>
                </tr>
            </thead>
            <tbody>
        <?php

        foreach ($available_products as $key => $value) {
            if (array_key_exists($key, $json_array[$requested_locale])) {
                $current_product = $json_array[$requested_locale][$key];
                $row_style = getRowStyle($current_product);
                echo "<tr class='{$row_style['class']}' style='{$row_style['style']}'>\n";
                echo '<th>' . $current_product['name'] . "</th>\n";
                echo '      <td class="number">' . $current_product['percentage'] . "</td>\n";
                echo '      <td class="number">' . $current_product['translated'] . "</td>\n";
                echo '      <td class="number">' . $current_product['untranslated'] . "</td>\n";
                echo '      <td class="number">' . $current_product['fuzzy'] . "</td>\n";
                echo '      <td class="number">' . $current_product['total'] . "</td>\n";
                echo '      <td>' . $current_product['error_message'] . "</td>\n";
                echo "</tr>\n";
            }
        }
        ?>
            </tbody>
        </table>
    <?php
    } else {
        // Display all locales for one product
        $completed_locales = 0;
        $total_locales = 0;

    ?>
        <h2><?php echo $available_products[$requested_product]; ?></h2>
        <table>
            <thead>
                <tr>
                    <th>Locale</th>
                    <th>%</th>
                    <th>Translated</th>
                    <th>Untransl.</th>
                    <th>Fuzzy</th>
                    <th>Total</th>
                    <th>Errors</th>
                </tr>
            </thead>
            <tbody>
        <?php
        foreach ($available_locales as $locale_code) {
            if (isset($json_array[$locale_code][$requested_product])) {
                $current_product = $json_array[$locale_code][$requested_product];
                if ($current_product['percentage'] == 100) {
                    $completed_locales++;
                }
                $total_locales++;

                $row_style = getRowStyle($current_product);
                echo "<tr class='{$row_style['class']}' style='{$row_style['style']}'>\n";
                echo "<th>{$locale_code}</th>\n";
                echo "      <td class='number'>{$current_product['percentage']}</td>";
                echo "      <td class='number'>{$current_product['translated']}</td>";
                echo "      <td class='number'>{$current_product['untranslated']}</td>";
                echo "      <td class='number'>{$current_product['fuzzy']}</td>";
                echo "      <td class='number'>{$current_product['total']}</td>";
                echo "      <td>{$current_product['error_message']}</td>";
                echo "</tr>\n";
            }
        }
        ?>
            </tbody>
        </table>
    <?php
        echo "<p>Complete locales: {$completed_locales} (total {$total_locales}).</p>";
    }
    ?>

<?php
    echo "<p>Last update: {$json_array['metadata']['creation_date']}</p>";
?>
</body>
</html>
