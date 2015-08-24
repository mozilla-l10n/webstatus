<?php
namespace tests\units\Webstatus;

use atoum;
use Webstatus\Utils as _Utils;

require_once __DIR__ . '/../bootstrap.php';

class Utils extends atoum\test
{
    public function testGetQueryParam()
    {
        $obj = new _Utils();

        $_GET['test_string'] = 'test';
        $_GET['test_bool'] = true;

        // Missing string param
        $this
            ->string($obj->getQueryParam('foo'))
                ->isEqualTo('');

        // Missing string param with fallback
        $this
            ->string($obj->getQueryParam('foo', 'bar'))
                ->isEqualTo('bar');

        // Existing param
        $this
            ->string($obj->getQueryParam('test_string'))
                ->isEqualTo('test');

        // Existing param
        $this
            ->boolean($obj->getQueryParam('test_bool', false))
                ->isTrue();

        // Missing boolean param
        $this
            ->boolean($obj->getQueryParam('foo', false))
                ->isFalse();

        unset($_GET['test_string']);
        unset($_GET['test_bool']);
    }

    public function getRowStyleDP()
    {
        return [
            ['100', '', 'style=\'background-color: rgba(129, 209, 25, 1);\''],
            ['90', 'mpstats', 'style=\'background-color: rgba(146, 204, 110, 0.7);\''],
            ['80', '', 'style=\'background-color: rgba(129, 209, 25, 0.6);\''],
            ['70', 'mpstats', 'style=\'background-color: rgba(146, 204, 110, 0.5);\''],
            ['50', '', 'style=\'background-color: rgba(255, 252, 61, 0.7);\''],
            ['40', 'mpstats', 'style=\'background-color: rgba(235, 235, 110, 0.8);\''],
            ['30', '', 'style=\'background-color: rgba(255, 194, 115, 0.7);\''],
            ['20', 'mpstats', 'style=\'background-color: rgba(255, 82, 82, 0.8);\''],
            ['10', '', 'style=\'background-color: rgba(255, 194, 115, 0.9);\''],
            ['0', 'mpstats', 'style=\'background-color: rgba(255, 82, 82, 1);\''],
        ];
    }

    /**
     * @dataProvider getRowStyleDP
     */
    public function testGetRowStyle($a, $b, $c)
    {
        $obj = new _Utils();
        $this
            ->string($obj->getRowStyle($a, $b))
                ->isEqualTo($c);
    }

    public function testDetectLocale()
    {
        $obj = new _Utils();

        $this
            ->string($obj->detectLocale())
                ->isEqualTo('en-US');

        $this
            ->string($obj->detectLocale([], 'en-GB'))
                ->isEqualTo('en-GB');

        $this
            ->string($obj->detectLocale(['fr', 'it'], 'en-US', 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3'))
                ->isEqualTo('it');

        $this
            ->string($obj->detectLocale(['ff', 'fr', 'it'], 'en-US', 'ff,fr-FR;q=0.8,fr;q=0.7,en-GB;q=0.5,en-US;q=0.3,en;q=0.2'))
                ->isEqualTo('ff');

        $this
            ->string($obj->detectLocale(['fr', 'it'], 'en-US', 'ff,fr-FR;q=0.8,fr;q=0.7,en-GB;q=0.5,en-US;q=0.3,en;q=0.2'))
                ->isEqualTo('fr');

        $this
            ->string($obj->detectLocale(['xh'], 'en-US', 'ff,fr-FR;q=0.8,fr;q=0.7,en-GB;q=0.5,en-US;q=0.3,en;q=0.2'))
                ->isEqualTo('en-US');
    }

    public function secureTextDP()
    {
        return [
            ['test%0D', false, 'test'],
            ['%0Atest', false, 'test'],
            ['%0Ate%0Dst', false, 'test'],
            ['%0Ate%0Dst', true, 'test'],
            ['&test', false, '&amp;test'],
            [['test%0D', '%0Atest'], false, 'test'],
        ];
    }

    /**
     * @dataProvider secureTextDP
     */
    public function testSecureText($a, $b, $c)
    {
        $obj = new _Utils();
        $this
            ->string($obj->secureText($a, $b))
                ->isEqualTo($c);
    }
}
