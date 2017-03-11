<?php
namespace Webstatus;

use Json\Json;

// Autoloading of composer dependencies
require_once __DIR__ . '/../../vendor/autoload.php';

mb_internal_encoding('UTF-8');
date_default_timezone_set('Europe/Paris');

// Set an environment variable so that the instance will use content from test files
putenv('AUTOMATED_TESTS=true');

// Launch PHP dev server in the background
$root_folder = realpath(__DIR__ . '/../../');
chdir("{$root_folder}/web");
exec('php -S 0.0.0.0:8083 > /dev/null 2>&1 & echo $!', $output);

// We will need the pid to kill it, beware, this is the pid of the php server started above
$pid = $output[0];

// Pause to let time for the dev server to launch in the background
sleep(3);

$failures = [];
$base_url = 'http://localhost:8083/api/';
$json_data = new Json;

// URL without parameters should return 400
$headers = get_headers($base_url, 1);
if (strpos($headers[0], '400 Bad Request') === false) {
    $failures[] = "HTTP status for URL without parameters is: {$headers[0]}. Expected: 400.";
}

// Query for unknown product
$url = $base_url . '?product=random';
$headers = get_headers($url, 1);
if (strpos($headers[0], '400 Bad Request') === false) {
    $failures[] = "HTTP status for unknown product is: {$headers[0]}. Expected: 400.";
}

// Query for existing product
$url = $base_url . '?product=browserid';
$headers = get_headers($url, 1);
if (strpos($headers[0], '200 OK') === false) {
    $failures[] = "HTTP status for known product (JSON) is: {$headers[0]}. Expected: 200.";
}

$response = $json_data
    ->setURI($url)
    ->fetchContent();
$expected_response = ['fr', 'it'];
if ($response != $expected_response) {
    $failures[] = 'Failure for api/?product=browserid' .
                  "\nResponse: " . implode(', ', $response) .
                  "\nExpected: " . implode(', ', $expected_response) . "\n";
}

// Check TXT version
$url .= '&txt';
$headers = get_headers($url, 1);
if (strpos($headers[0], '200 OK') === false) {
    $failures[] = "HTTP status for known product (TXT) is: {$headers[0]}. Expected: 200.";
}

$response = file_get_contents($url);
$expected_response = "fr\nit\n";
if ($response != $expected_response) {
    $failures[] = 'Failure for api/?product=browserid&txt' .
                  "\nResponse: \n" . $response .
                  "\nExpected: \n" . $expected_response . "\n";
}

// Query for existing product, incomplete locale
$url = $base_url . '?product=affiliates&type=incomplete';
$headers = get_headers($url, 1);
if (strpos($headers[0], '200 OK') === false) {
    $failures[] = "HTTP status for known product (JSON) is: {$headers[0]}. Expected: 200.";
}

$response = $json_data
    ->setURI($url)
    ->fetchContent();
$expected_response = ['fr'];
if ($response != $expected_response) {
    $failures[] = 'Failure for api/?product=affiliates&type=incomplete' .
                  "\nResponse: " . implode(', ', $response) .
                  "\nExpected: " . implode(', ', $expected_response) . "\n";
}

// Check TXT version
$url .= '&txt';
$headers = get_headers($url, 1);
if (strpos($headers[0], '200 OK') === false) {
    $failures[] = "HTTP status for known product (TXT) is: {$headers[0]}. Expected: 200.";
}

$response = file_get_contents($url);
$expected_response = "fr\n";
if ($response != $expected_response) {
    $failures[] = 'Failure for api/?product=affiliates&type=incomplete&txt' .
                  "\nResponse: \n" . $response .
                  "\nExpected: \n" . $expected_response . "\n";
}

// Query for existing product, complete locale
$url = $base_url . '?product=browserid&type=complete';
$headers = get_headers($url, 1);
if (strpos($headers[0], '200 OK') === false) {
    $failures[] = "HTTP status for known product (JSON) is: {$headers[0]}. Expected: 200.";
}

$response = $json_data
    ->setURI($url)
    ->fetchContent();
$expected_response = ['fr'];
if ($response != $expected_response) {
    $failures[] = 'Failure for api/?product=browserid&type=complete' .
                  "\nResponse: " . implode(', ', $response) .
                  "\nExpected: " . implode(', ', $expected_response) . "\n";
}

// Check TXT version
$url .= '&txt';
$headers = get_headers($url, 1);
if (strpos($headers[0], '200 OK') === false) {
    $failures[] = "HTTP status for known product (TXT) is: {$headers[0]}. Expected: 200.";
}

$response = file_get_contents($url);
$expected_response = "fr\n";
if ($response != $expected_response) {
    $failures[] = 'Failure for api/?product=browserid&type=complete&txt' .
                  "\nResponse: \n" . $response .
                  "\nExpected: \n" . $expected_response . "\n";
}

// Kill PHP dev server we launched in the background
exec('kill -9 ' . $pid);

// Display results
if ($failures) {
    echo Utils::colorizeOutput('Functional test: FAILURES (' . count($failures) . ')', 'red');
    echo implode("\n", $failures);
    echo "\n";
    exit(1);
} else {
    echo Utils::colorizeOutput('Functional tests: PASSED.', 'green');
}
