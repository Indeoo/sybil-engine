import unittest

from sybil_engine.module.execution_planner import create_execution_plans
from test import zksync_test_account
from test.test_config import create_config

mock = {
    'scenario_name': 'TEST_module_0_config',
    'scenario': [
        {
            'module': 'MockModule',
            'params': {
            }
        },
        {
            'module': 'MockModule',
            'params': {
            }
        }
    ]
}


class TestExecutionPlanner(unittest.TestCase):

    def test_should_form_execution_planner(self):
        modules, encryption, min_native_interval, proxy_config, okx_config, sleep_interval, swap_retry_sleep_interval, gas_prices_gwei = create_config()

        create_execution_plans(
            [zksync_test_account],
            min_native_interval,
            mock,
            modules
        )
