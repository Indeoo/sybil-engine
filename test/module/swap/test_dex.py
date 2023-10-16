import unittest

from sybil_engine.data.networks import get_chain_instance
from sybil_engine.domain.balance.balance import NativeBalance
from sybil_engine.utils.utils import SwapException
from sybil_engine.utils.web3_utils import init_web3
from test import zksync_test_account, init_set_test_config
from test.module.swap.mock_dex import MockFailDex


class TestDex(unittest.TestCase):
    init_set_test_config()

    def test_succeed_after_3_retries(self):
        chain_instance = get_chain_instance('ZKSYNC')
        web3 = init_web3(chain_instance, None)
        from_token = 'ETH'
        to_token = 'USDC'
        slippage = 0.99
        amount_to_swap = NativeBalance(10000000, 'ZKSYNC', 'ETH')

        test_dex = MockFailDex(chain_instance, web3, 2, {'from': 1, 'to': 2})

        test_dex.swap_with_retry(amount_to_swap, from_token, to_token, slippage, zksync_test_account)

    def test_fail_after_3_retries(self):
        chain_instance = get_chain_instance('ZKSYNC')
        web3 = init_web3(chain_instance, None)
        from_token = 'ETH'
        to_token = 'USDC'
        slippage = 0.99
        amount_to_swap = NativeBalance(10000000, 'ZKSYNC', 'ETH')

        test_dex = MockFailDex(chain_instance, web3, 3, {'from': 1, 'to': 2})

        with self.assertRaises(SwapException):
            test_dex.swap_with_retry(amount_to_swap, from_token, to_token, slippage, zksync_test_account)
