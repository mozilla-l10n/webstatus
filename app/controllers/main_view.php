<?php
namespace Webstatus;

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
