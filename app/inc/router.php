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
        $controller = 'api';
        break;
    case "{$base_url}mpstats":
        $controller = 'mpstats';
        break;
    case "{$base_url}views/xliff_diff.php":
        $controller = 'xliff_diff';
        $view = 'xliff_diff';
        break;
    case $base_url:
        $controller = 'main_view';
        $view = 'main_view';
        break;
    case $webroot_folder:
        $controller = 'main_view';
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

if (isset($controller)) {
    include __DIR__ . "/../controllers/{$controller}.php";
}

if (isset($view)) {
    include __DIR__ . "/../views/{$view}.php";
}
