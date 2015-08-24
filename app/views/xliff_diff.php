<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset=utf-8>
    <title>Web Status - XLIFF Comparison</title>
<?php
foreach ($default_css as $css_filename) {
    echo "    <link rel=\"stylesheet\" href=\"{$assets_folder}/css/{$css_filename}\" type=\"text/css\" media=\"all\" />\n";
}
?>
</head>
<body>
  <div class="container">
<?php
if ($error_messages != '') {
    echo "<h1>Error</h1>\n{$error_messages}";
} else {
    echo $html_output;
}
?>
  </div>
</body>
</html>
