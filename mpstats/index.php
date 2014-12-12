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

$excluded_locales = ['an', 'ak', 'az', 'br', 'db-LB', 'dsb', 'en', 'en-GB',
                     'en-US', 'en-ZA', 'es-AR', 'es-CL', 'es-ES', 'es-MX',
                     'fur', 'fy', 'ga', 'gu-IN', 'hsb', 'hy-AM', 'is',
                     'ja-JP-mac', 'kk', 'lv', 'mai', 'mr', 'nb', 'nn-NO',
                     'no', 'oc', 'pa-IN', 'pt', 'rm', 'rw', 'sah', 'son',
                     'sr-CYRL', 'sr-LATN', 'sv', 'sw', 'ta-LK',
                     'zh-Hant-TW', 'metadata'];

// Extract locales
$locales = [];
foreach ($json_array as $locale => $product) {
    array_push($locales, $locale);
}
sort($locales);
// Exclude some locales
$locales = array_diff($locales, $excluded_locales);

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
    <link rel="stylesheet" href="../css/mpstats.css" type="text/css" media="all" />
    <script src="../js/jquery-1.11.1.min.js"></script>
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
                $(row).before('<tr class="spacer top" colspan="<?php echo $columns_number;?>">&nbsp;</tr>');
                $(row).after('<tr class="spacer bottom" colspan="<?php echo $columns_number;?>">&nbsp;</tr>');
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
<?php
    $content = "<table>\n";
    $content .= "  <thead>\n";
    $content .= "     <tr>\n";
    $content .= "       <th>&nbsp;</th>\n";
    foreach ($products as $code => $name) {
        $content .= "       <th colspan='3'>{$name}</th>\n";
    }
    $content .= "     </tr>\n";
    $content .= "     <tr>\n";
    $content .= "       <th>Locale</th>\n";
    for ($i=0; $i < count($products); $i++) {
        $content .= "       <th class='firstsection'>trans.</th>\n";
        $content .= "       <th>untr.</th>\n";
        $content .= "       <th class='lastsection'>%</th>\n";
    }
    $content .= "     </tr>\n";
    $content .= "   </thead>\n";
    $content .= "   <tbody>\n";
    foreach ($locales as $locale) {
        $content .= "     <tr id='row_{$locale}'>\n";
        $content .= "       <th class='rowheader'><a href='#{$locale}' id='{$locale}' class='locale_anchor'>{$locale}</a></th>\n";
        foreach ($products as $code => $name) {
            if (array_key_exists($code, $json_array[$locale])) {
                $current_product = $json_array[$locale][$code];
                $content .= "       <td class='firstsection' " . getRowStyle($current_product) . ">{$current_product['translated']}</td>\n";
                $content .= "       <td " . getRowStyle($current_product) . ">{$current_product['untranslated']}</td>\n";
                $content .= "       <td class='lastsection' " . getRowStyle($current_product) . ">{$current_product['percentage']}</td>\n";
            } else {
                // Missing products
                $content .= "       <td colspan='3'>&nbsp;</td>\n";
            }

        }
        $content .= "     </tr>\n";
    }
    $content .= "   </tbody>\n";
    $content .= " </table>\n";
    $content .= "<p class='lastupdate'>Last update: {$json_array['metadata']['creation_date']}</p>";
    echo $content;
?>
</body>
</html>