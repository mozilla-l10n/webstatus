<?php
namespace Webstatus;

/**
 * Utils class
 *
 * Collection of static methods
 *
 *
 * @package Webstatus
 */
class Utils
{
    /**
     * Read GET parameter if set, or fallback
     *
     * @param string $param    GET parameter to check
     * @param string $fallback Optional fallback value
     *
     * @return string Parameter value, or fallback
     */
    public static function getQueryParam($param, $fallback = '')
    {
        if (isset($_GET[$param])) {
            return is_bool($fallback)
                   ? true
                   : self::secureText($_GET[$param]);
        }

        return $fallback;
    }

    /**
     * Try to get the best supported locale from HTTP_ACCEPT_LANGUAGE header
     *
     * @param array  $available_locales Available locales
     * @param string $fallback_locale   Fallback locale
     * @param string $header            HTTP_ACCEPT_LANGUAGE header
     *
     * @return string Best supported locale code
     */
    public static function detectLocale($available_locales = [], $fallback_locale = 'en-US', $header = '')
    {
        $accept_languages = [];
        if ($header == '') {
            // Read the header from the server, if available
            $header = isset($_SERVER['HTTP_ACCEPT_LANGUAGE']) ? $_SERVER['HTTP_ACCEPT_LANGUAGE'] : '';
        }
        // Source: http://www.thefutureoftheweb.com/blog/use-accept-language-header
        if ($header != '') {
            // Break up string into pieces (languages and q factors)
            preg_match_all(
                '/([a-z]{1,8}(-[a-z]{1,8})?)\s*(;\s*q\s*=\s*(1|0\.[0-9]+))?/i',
                $header,
                $lang_parse
            );
            if (count($lang_parse[1])) {
                // Create a list like "en" => 0.8
                $accept_languages = array_combine($lang_parse[1], $lang_parse[4]);
                // Set default to 1 for any without q factor
                foreach ($accept_languages as $accept_locale => $val) {
                    if ($val === '') {
                        $accept_languages[$accept_locale] = 1;
                    }
                }
                // Sort list based on value
                arsort($accept_languages, SORT_NUMERIC);
            }
        }

        // Check if any of the locales is available
        $intersection = array_values(array_intersect(array_keys($accept_languages), $available_locales));
        if (! isset($intersection[0])) {
            // Accept-Language doesn't include any supported locale
            return $fallback_locale;
        } else {
            return $intersection[0];
        }
    }

    /**
     * Return inline style (color, opacity) for a row based on
     * the level of translation
     *
     * @param string $percentage Percentage of translated strings
     * @param string $view       Which view it's currently displayed
     *
     * @return array Inline CSS colors for the given percentage
     */
    public static function getRowStyle($percentage, $view = 'main')
    {
        // $base_colors store the 3 base RGB colors
        $base_colors = [];
        if ($view == 'mpstats') {
            $base_colors = [
                'green'  => '146, 204, 110',
                'yellow' => '235, 235, 110',
                'red'    => '255, 82, 82',
            ];
        } else {
            $base_colors = [
                'green'  => '129, 209, 25',
                'yellow' => '255, 252, 61',
                'red'    => '255, 194, 115',
            ];
        }

        if ($percentage < 100) {
            $opacity = floor(round(($percentage - 20) / 100, 2) * 10) / 10;
        } else {
            $opacity = 1;
        }

        if ($percentage >= 70) {
            $color = 'green';
        } elseif ($percentage >= 40) {
            $opacity = 1 - $opacity;
            $color = 'yellow';
        } else {
            $opacity = 0.8 - $opacity;
            $color = 'red';
        }
        $stylerow = "style='background-color: rgba({$base_colors[$color]}, {$opacity});'";

        return $stylerow;
    }

    /**
     * Function sanitizing a string or an array of strings.
     *
     * @param mixed   $origin  String/Array of strings to sanitize
     * @param boolean $isarray If $origin must be treated as array
     *
     * @return mixed Sanitized string or array
     */
    public static function secureText($origin, $isarray = true)
    {
        if (! is_array($origin)) {
            // If $origin is a string, always return a string
            $origin  = [$origin];
            $isarray = false;
        }

        foreach ($origin as $item => $value) {
            // CRLF XSS
            $item  = str_replace('%0D', '', $item);
            $item  = str_replace('%0A', '', $item);
            $value = str_replace('%0D', '', $value);
            $value = str_replace('%0A', '', $value);

            $value = filter_var(
                $value,
                FILTER_SANITIZE_STRING,
                FILTER_FLAG_STRIP_LOW
            );

            $item  = htmlspecialchars(strip_tags($item), ENT_QUOTES);
            $value = htmlspecialchars(strip_tags($value), ENT_QUOTES);

            // Repopulate value
            $sanitized[$item] = $value;
        }

        return ($isarray == true) ? $sanitized : $sanitized[0];
    }
}
