<?php

// Twig settings
$templates = new Twig_Loader_Filesystem(__DIR__ . '/../templates/');
$options = [
    'cache' => false,
];
$twig = new Twig_Environment($templates, $options);

$twig->addGlobal('assets_folder', $assets_folder);
$twig->addGlobal('last_update', $last_update_local);
