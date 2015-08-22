<?php

// Load init file
require __DIR__ . '/init.php';

$url = parse_url($_SERVER['REQUEST_URI']);

if ($url['path'] != '/') {
    // Normalize path before comparing the string to list of valid paths
    $url['path'] = explode('/', $url['path']);
    $url['path'] = array_filter($url['path']); // Remove empty items
    $url['path'] = array_values($url['path']); // Reorder keys
    $url['path'] = implode('/', $url['path']);
} else {
    $url['path'] = '';
}

$base_url = ($webroot_folder == '') ? '' : "{$webroot_folder}/";

$unknown_url = false;
switch ($url['path']) {
    case "{$base_url}api":
        $view = 'api';
        break;
    case "{$base_url}mpstats":
        $view = 'mpstats';
        break;
    case "{$base_url}views/xliff_diff.php":
        $view = 'xliff_diff';
        break;
    case $base_url:
        $view = 'main_view';
        break;
    case $webroot_folder:
        $view = 'main_view';
        break;
    default:
        $unknown_url = true;
        break;
}

if ($unknown_url) {
    // Unknown, redirect to main URL
    echo "Need redirect<br>";
    header("Location: /{$webroot_folder}");
    die();
}

include __DIR__ . "/../views/{$view}.php";
