<?php
namespace Webstatus;

/**
 * Webstatus class
 *
 * Main Webstatus class
 *
 *
 * @package Webstatus
 */
class Webstatus
{
    /**
     * @var array $webstatus_data Store the decoded JSON file with full
     *            webstatus data
     */
    private $webstatus_data = [];

    /**
     * @var array $sources_data Store the decoded JSON file with sources data
     */
    private $sources_data = [];

    /**
     * Build Webstatus object and load data internally
     *
     * @param string $json_file    URI of the JSON file with full Webstatus data
     * @param string $sources_file URI of the JSON file with sources data
     */
    public function __construct($json_file, $sources_file)
    {
        if (file_exists($json_file)) {
            $this->webstatus_data = json_decode(file_get_contents($json_file), true);
        } else {
            die('JSON file is missing. Have you run app/scripts/webstatus.py at least once?');
        }
        if (file_exists($sources_file)) {
            $this->sources_data = json_decode(file_get_contents($sources_file), true);
        }
    }

    /**
     * Return list of available locales
     *
     * @return array List of available locales, sorted alphabetically
     */
    public function getAvailableLocales()
    {
        $supported_locales = array_keys($this->webstatus_data['locales']);
        sort($supported_locales);

        return $supported_locales;
    }

    /**
     * Return list of available products
     *
     * @return array List of available products, sorted alphabetically by name
     */
    public function getAvailableProducts()
    {
        $available_products = $this->webstatus_data['metadata']['products'];
        // Sort elements based on 'name'
        uasort($available_products, function ($a, $b) {
            return ($a < $b) ? -1 : 1;
        });

        // Add 'All products'
        $product_all = [
            'all' => [
                'name'            => 'All products',
                'repository_type' => '',
                'repository_url'  => '',
            ],
        ];

        // Using union to make sure "all" is the first product
        $available_products = $product_all + $available_products;

        return $available_products;
    }

    /**
     * Return data for all products and locales
     *
     * @return array Data for all locales and products
     */
    public function getWebstatusData()
    {
        return $this->webstatus_data['locales'];
    }

    /**
     * Return metadata (product list, last update date)
     *
     * @return array Metadata for webstatus
     */
    public function getWebstatusMetadata()
    {
        return $this->webstatus_data['metadata'];
    }

    /**
     * Return the product data (source type, path, etc.)
     *
     * @param string $product_id Product ID to check
     *
     * @return array Complete array of product data
     */
    public function getSingleProductData($product_id)
    {
        if (! isset($this->sources_data[$product_id])) {
            return [];
        }

        return $this->sources_data[$product_id];
    }

    /**
     * Return the source type of a product (properties, gettext, etc.)
     *
     * @param string $product_id Product ID to check
     *
     * @return string Source type for the requested product
     */
    public function getSourceType($product_id)
    {
        return $this->sources_data[$product_id]['source_type'];
    }
}
