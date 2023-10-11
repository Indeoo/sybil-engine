import unittest

from loguru import logger
from sybil_engine.app import process_accounts
from test import zksync_test_account

from test.module.mock_fail_module import MockFailModule
from test.module.mock_module import MockModule
from test.test_config import create_config

warmup_test_config = {
    'auto_withdrawal': True,
    'chain': 'ZKSYNC',
    'swap_amount_interval': {'from': 1, 'to': 1},
    'token': 'ETH',
    'amount_of_warmups': {'from': 1, 'to': 3},
    'allowed_dex': ['syncswap', 'mute', 'woofi', 'maverick', 'velocore', 'lineaswap', 'pancake', 'odos'],
    'warmup_pairs': '',  # specify for warming up by concrete pair
    'sell_tokens': True,
    'pair_sleep_interval': {'from': 0, 'to': 0}  # Interval between different tokens warm up of 1 account
}


class TestApp(unittest.TestCase):

    def test_should_return_empty_skipp_acc_on_success(self):
        logger.info("Test process_accounts")
        modules, encryption, min_native_interval, proxy_config, okx_config, sleep_interval, swap_retry_sleep_interval, gas_prices_gwei = create_config()

        try:
            self.assertFalse(
                process_accounts([zksync_test_account],
                                 None,
                                 min_native_interval,
                                 [(MockModule, {})],
                                 okx_config,
                                 sleep_interval)
            )
        except Exception as e:
            self.fail(f"Some function raised an exception: {e}")

    def test_should_add_acc_to_skip_on_fail(self):
        logger.info("Test process_accounts")

        modules, encryption, min_native_interval, proxy_config, okx_config, sleep_interval, swap_retry_sleep_interval, gas_prices_gwei = create_config()

        try:
            self.assertEqual(
                [zksync_test_account],
                process_accounts([zksync_test_account], None, min_native_interval, [(MockFailModule, {})], okx_config,
                                 sleep_interval))
        except Exception as e:
            self.fail(f"Some function raised an exception: {e}")
