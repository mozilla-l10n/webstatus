<?php
namespace Webstatus;

?>
<!DOCTYPE html>
<html lang="en-US">
<head>
    <meta charset=utf-8>
    <title>Marketplace Status</title>
<?php
array_push($default_css, 'mpstats.css');
foreach ($default_css as $css_filename) {
    echo "    <link rel=\"stylesheet\" href=\"{$assets_folder}/css/{$css_filename}\" type=\"text/css\" media=\"all\" />\n";
}

array_push($default_js, 'mpstats.js');
foreach ($default_js as $js_filename) {
    echo "    <script src=\"{$assets_folder}/js/{$js_filename}\"></script>\n";
}
?>
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
                $content .= "       <td " . Utils::getRowStyle($current_product['percentage'], 'mpstats') . ">{$current_product['translated']}</td>\n" .
                            "       <td " . Utils::getRowStyle($current_product['percentage'], 'mpstats') . ">{$current_product['untranslated']}</td>\n" .
                            "       <td " . Utils::getRowStyle($current_product['percentage'], 'mpstats') . ">{$current_product['percentage']}</td>\n";
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
