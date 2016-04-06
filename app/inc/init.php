<?php
namespace Webstatus;

date_default_timezone_set('Europe/Paris');
require __DIR__ . '/../../vendor/autoload.php';

$root_folder = realpath(__DIR__ . '/../..');

if (getenv('AUTOMATED_TESTS')) {
    $config_file = "{$root_folder}/app/config/config.ini-dist";
    $sources_file = "{$root_folder}/tests/testfiles/config/sources.json";
    $webstatus_file = "{$root_folder}/tests/testfiles/config/webstatus_test.json";
} else {
    $config_file = "{$root_folder}/app/config/config.ini";
    $sources_file = "{$root_folder}/app/config/sources.json";
    $webstatus_file = "{$root_folder}/web/web_status.json";
}

// Store server config
$server_config = parse_ini_file($config_file);
$webroot_folder = isset($server_config['web_folder']) ? trim($server_config['web_folder']) : '';
$assets_folder = $webroot_folder != '' ? "/{$webroot_folder}/assets" : '/assets';

// Base variables
$webstatus = new Webstatus($webstatus_file, $sources_file);
$available_locales = $webstatus->getAvailableLocales();
$available_products =  $webstatus->getAvailableProducts();
$webstatus_data = $webstatus->getWebstatusData();
$webstatus_metadata = $webstatus->getWebstatusMetadata();
$requested_locale = Utils::getQueryParam('locale', Utils::detectLocale($available_locales));
$requested_product = Utils::getQueryParam('product', 'all');

$last_update_local = date('Y-m-d H:i e (O)', strtotime($webstatus_metadata['creation_date']));

require_once __DIR__ . '/twig_init.php';
