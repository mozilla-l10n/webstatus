<?php

date_default_timezone_set('Europe/Rome');

$json_filename = '../webstatus.json';
$json_array = (array) json_decode(file_get_contents($json_filename), true);

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
    'es-AR', 'es-CL', 'es-ES', 'es-MX', 'fur', 'fy', 'ga', 'gu-IN',
    'hy-AM', 'is', 'kk', 'lv', 'mai', 'metadata', 'mr', 'nb', 'nn-NO',
    'no', 'oc', 'pa-IN', 'pt', 'rm', 'rw', 'sah', 'son', 'sr-Cyrl',
    'sr-CYRL', 'sr-LATN', 'sv', 'ta-LK'
];

// Extract locales and exclude some of them
$locales = array_keys($json_array);
$locales = array_diff($locales, $excluded_locales);
sort($locales);

// Extract product names from en-US
foreach ($json_array['en-US'] as $code => $product) {
    if (array_key_exists($code, $products)) {
        $products[$code] = $product['name'];
    }
}

function getRowStyle($current_product) {
    $perc = $current_product['percentage'];
    $opacity = 1;
    if ($perc < 100) {
        $opacity = floor(round(($perc-20)/100,2)*10)/10;
    }
    if ($perc >= 70) {
        $stylerow = "background-color: rgba(146, 204, 110, {$opacity});";
    } elseif ($perc >= 40) {
        $opacity = 1 - $opacity;
        $stylerow = "background-color: rgba(235, 235, 110, {$opacity});";
    } else {
        $opacity = 1 - $opacity;
        $stylerow = "background-color: rgba(255, 82, 82, {$opacity});";
    }
    $stylerow = "style='{$stylerow}'";
    return $stylerow;
}

$columns_number = 1 + 3 * count($products);
?>

<!DOCTYPE html>
<html lang="en-US">
<head>
    <meta charset=utf-8>
    <title>Marketplace Status</title>
    <link rel="stylesheet" href="../assets/css/bootstrap.min.css" type="text/css" media="all" />
    <link rel="stylesheet" href="../assets/css/bootstrap-theme.min.css" type="text/css" media="all" />
    <link rel="stylesheet" href="../assets/css/mpstats.css" type="text/css" media="all" />
    <script src="../assets/js/jquery-1.11.1.min.js"></script>
    <script type="text/javascript">
        $(document).ready(function() {
            // Associate click handlers to anchors
            $('.locale_anchor').click(function (e) {
                e.preventDefault;
                // Remove other selected rows and spacers
                $('tr').removeClass('selected');
                $('.spacer').remove();

                // Add empty row before and after this element
                var row = '#row_' + e.target.id;
                $(row).before('<tr class="spacer_top" colspan="<?php echo $columns_number;?>">&nbsp;</tr>');
                $(row).after('<tr class="spacer_bottom" colspan="<?php echo $columns_number;?>">&nbsp;</tr>');
                // Add selected class to this row
                $(row).addClass('selected');
                // Scroll slight above the anchor
                var y = $(window).scrollTop();
                $("html, body").animate(
                    {
                        scrollTop: y - 150
                    }, 500);
            });

            var anchor = location.hash.substring(1);
            if (anchor !== '') {
                $('#' + anchor).click();
            }
        });
    </script>
</head>

<body>
<div class="container">
  <h1>Marketplace Projects l10n Overview</h1>
<?php
    $content = "<table class='table table-bordered table-condensed'>\n" .
               "  <thead>\n" .
               "     <tr>\n" .
               "       <th>&nbsp;</th>\n";
    foreach ($products as $code => $name) {
        $content .= "       <th colspan='3'>{$name}</th>\n";
    }
    $content .= "     </tr>\n" .
                "     <tr>\n" .
                "       <th>Locale</th>\n";
    for ($i=0; $i < count($products); $i++) {
        $content .= "       <th>trans.</th>\n" .
                    "       <th>untr.</th>\n" .
                    "       <th>%</th>\n";
    }
    $content .= "     </tr>\n" .
                "   </thead>\n" .
                "   <tbody>\n";
    foreach ($locales as $locale) {
        $content .= "     <tr id='row_{$locale}'>\n" .
                    "       <th class='rowheader'><a href='#{$locale}' id='{$locale}' class='locale_anchor'>{$locale}</a></th>\n";
        foreach ($products as $code => $name) {
            if (array_key_exists($code, $json_array[$locale])) {
                $current_product = $json_array[$locale][$code];
                $content .= "       <td " . getRowStyle($current_product) . ">{$current_product['translated']}</td>\n" .
                            "       <td " . getRowStyle($current_product) . ">{$current_product['untranslated']}</td>\n" .
                            "       <td " . getRowStyle($current_product) . ">{$current_product['percentage']}</td>\n";
            } else {
                // Missing products
                $content .= "       <td colspan='3'>&nbsp;</td>\n";
            }

        }
        $content .= "     </tr>\n";
    }
    $content .= "   </tbody>\n" .
                " </table>\n" .
                "<p class='lastupdate'>Last update: {$json_array['metadata']['creation_date']}</p>";
    echo $content;
?>
</div>
</body>
</html>