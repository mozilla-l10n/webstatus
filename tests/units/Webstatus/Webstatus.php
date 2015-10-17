<?php
namespace tests\units\Webstatus;

use atoum;
use Webstatus\Webstatus as _Webstatus;

require_once __DIR__ . '/../bootstrap.php';

class Webstatus extends atoum\test
{
    public function testGetAvailableLocales()
    {
        $obj = new _Webstatus(TEST_FILES . 'config/webstatus_test.json', TEST_FILES . 'config/sources.json');

        $this
            ->array($obj->getAvailableLocales())
                ->isEqualTo(['en-US', 'fr', 'it']);
    }

    public function testGetAvailableProducts()
    {
        $obj = new _Webstatus(TEST_FILES . 'config/webstatus_test.json', TEST_FILES . 'config/sources.json');

        $available_products = $obj->getAvailableProducts();
        $test_product = [
            'name'            => 'Firefox Affiliates',
            'repository_type' => 'svn',
            'repository_url'  => 'http://svn.mozilla.org/projects/l10n-misc/trunk/affiliates/',
        ];
        $product_ids = ['all', 'browserid', 'affiliates', 'zippy'];

        $this
            ->array(array_keys($available_products))
                ->isEqualTo($product_ids);

        $this
            ->array($available_products['affiliates'])
                ->isEqualTo($test_product);
    }

    public function testGetSingleProductData()
    {
        $obj = new _Webstatus(TEST_FILES . 'config/webstatus_test.json', TEST_FILES . 'config/sources.json');

        $test_product = [
            'displayed_name'   => 'Firefox Affiliates',
            'excluded_folders' => [],
            'locale_folder'    => 'locale',
            'product_name'     => 'affiliates',
            'repository_name'  => 'affiliates',
            'repository_type'  => 'svn',
            'repository_url'   => 'http://svn.mozilla.org/projects/l10n-misc/trunk/affiliates/',
            'source_files'     => ['LC_MESSAGES/messages.po'],
            'source_type'      => 'xliff',
        ];

        $this
            ->array($obj->getSingleProductData('affiliates'))
                ->isEqualTo($test_product);
    }

    public function getSourceTypeDP()
    {
        return [
            ['affiliates', 'xliff'],
            ['browserid', 'properties'],
            ['zippy', 'gettext'],
        ];
    }

    /**
     * @dataProvider getSourceTypeDP
     */
    public function testGetSourceType($a, $b)
    {
        $obj = new _Webstatus(TEST_FILES . 'config/webstatus_test.json', TEST_FILES . 'config/sources.json');
        $this
            ->string($obj->getSourceType($a))
                ->isEqualTo($b);
    }

    public function testGetWebstatusData()
    {
        $obj = new _Webstatus(TEST_FILES . 'config/webstatus_test.json', TEST_FILES . 'config/sources.json');
        $reference_data = json_decode(file_get_contents(TEST_FILES . 'config/webstatus_test.json'), true);

        $this
            ->array($obj->getWebstatusData())
                ->isEqualTo($reference_data['locales']);
    }

    public function testGetWebstatusMetadata()
    {
        $obj = new _Webstatus(TEST_FILES . 'config/webstatus_test.json', TEST_FILES . 'config/sources.json');
        $reference_data = json_decode(file_get_contents(TEST_FILES . 'config/webstatus_test.json'), true);

        $this
            ->array($obj->getWebstatusMetadata())
                ->isEqualTo($reference_data['metadata']);
    }
}
