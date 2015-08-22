<?php

date_default_timezone_set('Europe/Paris');
require __DIR__ . '/../../vendor/autoload.php';

$root_folder = __DIR__ . '/../..';

$config_file = "{$root_folder}/app/config/config.ini";
$sources_file = "{$root_folder}/app/config/sources.json";
$webstatus_file = "{$root_folder}/web_status.json";

// Store server config
$server_config = parse_ini_file($config_file);

$webroot_folder = isset($server_config['web_folder']) ? trim($server_config['web_folder']) : '';
$assets_folder = $webroot_folder != '' ? "/{$webroot_folder}/web/assets" : '/web/assets';
