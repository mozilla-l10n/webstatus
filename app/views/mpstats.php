<?php
namespace Webstatus;

$webstatus = new Webstatus($webstatus_file, $sources_file);
$available_locales = $webstatus->getAvailableLocales();
$available_products =  $webstatus->getAvailableProducts();
$webstatus_data = $webstatus->getWebstatusData();
$webstatus_metadata = $webstatus->getWebstatusMetadata();

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
    'es-AR', 'es-CL', 'es-ES', 'es-MX', 'fur', 'fy', 'fy-NL', 'ga', 'gu-IN',
    'hy-AM', 'is', 'kk', 'lv', 'mai', 'metadata', 'mr', 'nb', 'nn-NO',
    'no', 'oc', 'pa-IN', 'pt', 'rm', 'rw', 'sah', 'son', 'sr-Cyrl',
    'sr-CYRL', 'sr-LATN', 'sv', 'ta-LK', 'uz',
];

// Extract locales and exclude some of them
$locales = array_diff($available_locales, $excluded_locales);

// Extract product names
foreach ($webstatus_metadata['products'] as $product_id => $product) {
    if (isset($products[$product_id])) {
        $products[$product_id] = $product['name'];
    }
}

function getRowStyle($current_product)
{
    $perc = $current_product['percentage'];
    $opacity = 1;
    if ($perc < 100) {
        $opacity = floor(round(($perc - 20) / 100, 2) * 10) / 10;
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
    <link rel="stylesheet" href="<?=$assets_folder?>/css/bootstrap.min.css" type="text/css" media="all" />
    <link rel="stylesheet" href="<?=$assets_folder?>/css/bootstrap-theme.min.css" type="text/css" media="all" />
    <link rel="stylesheet" href="<?=$assets_folder?>/css/dataTables.bootstrap.css" type="text/css" media="all" />
    <link rel="stylesheet" href="<?=$assets_folder?>/css/mpstats.css" type="text/css" media="all" />
    <script src="<?=$assets_folder?>/js/jquery-1.11.3.min.js"></script>
    <script src="<?=$assets_folder?>/js/jquery.dataTables.min.js"></script>
    <script src="<?=$assets_folder?>/js/dataTables.bootstrap.min.js"></script>
    <script type="text/javascript">
        $(document).ready(function () {
            // Make table sortable
            $('#main_table').DataTable({
                info: false,
                paging: false,
                searching: false
            });

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
    $content = "<table id='main_table' class='table table-bordered table-condensed'>\n" .
               "  <thead>\n" .
               "     <tr>\n" .
               "       <th>&nbsp;</th>\n";
    foreach ($products as $code => $name) {
        $content .= "       <th colspan='3'>{$name}</th>\n";
    }
    $content .= "     </tr>\n" .
                "     <tr>\n" .
                "       <th>Locale</th>\n";
    for ($i = 0; $i < count($products); $i++) {
        $content .= "       <th><abbr title='Translated'>Tr.</abbr></th>\n" .
                    "       <th><abbr title='Untranslated'>Un.</abbr></th>\n" .
                    "       <th><abbr title='Completion percentage'>%</abbr></th>\n";
    }
    $content .= "     </tr>\n" .
                "   </thead>\n" .
                "   <tbody>\n";
    foreach ($locales as $locale) {
        $content .= "     <tr id='row_{$locale}'>\n" .
                    "       <th class='rowheader'><a href='#{$locale}' id='{$locale}' class='locale_anchor'>{$locale}</a></th>\n";
        foreach ($products as $code => $name) {
            if (array_key_exists($code, $webstatus_data[$locale])) {
                $current_product = $webstatus_data[$locale][$code];
                $content .= "       <td " . getRowStyle($current_product) . ">{$current_product['translated']}</td>\n" .
                            "       <td " . getRowStyle($current_product) . ">{$current_product['untranslated']}</td>\n" .
                            "       <td " . getRowStyle($current_product) . ">{$current_product['percentage']}</td>\n";
            } else {
                // Missing products
                $content .= "       <td> </td>\n" .
                            "       <td> </td>\n" .
                            "       <td> </td>\n";
            }
        }
        $content .= "     </tr>\n";
    }

    $last_update_local = date('Y-m-d H:i e (O)', strtotime($webstatus_metadata['creation_date']));
    $content .= "   </tbody>\n" .
                " </table>\n" .
                "<p class='lastupdate'>Last update: {$last_update_local}</p>";
    echo $content;
?>
</div>
</body>
</html>
