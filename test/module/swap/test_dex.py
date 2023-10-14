import unittest

from sybil_engine.config.app_config import set_network
from sybil_engine.data.contracts import get_contracts_for_chain
from sybil_engine.data.networks import get_chain_instance
from sybil_engine.data.tokens import get_tokens_for_chain
from sybil_engine.utils.utils import SwapException
from sybil_engine.utils.web3_utils import init_web3

from core.modules.stargate.stargate_balance_utils import NativeBalance
from tests.core.modules import zksync_test_account
from tests.core.modules.swap.mock_dex import MockDex


class TestDex(unittest.TestCase):
    set_network('LOCAL')

    def test_succeed_after_3_retries(self):
        chain_contracts = get_contracts_for_chain("ZKSYNC")
        tokens = get_tokens_for_chain('ZKSYNC')
        chain_instance = get_chain_instance('ZKSYNC')
        web3 = init_web3(chain_instance, None)
        from_token = 'ETH'
        to_token = 'USDC'
        slippage = 0.99
        amount_to_swap = NativeBalance(10000000, 'ZKSYNC', 'ETH')

        test_dex = MockDex(chain_contracts, tokens, chain_instance, web3, 2, {'from': 1, 'to': 2})

        test_dex.swap_with_retry(amount_to_swap, from_token, to_token, slippage, zksync_test_account)

    def test_fail_after_3_retries(self):
        chain_contracts = get_contracts_for_chain("ZKSYNC")
        tokens = get_tokens_for_chain('ZKSYNC')
        chain_instance = get_chain_instance('ZKSYNC')
        web3 = init_web3(chain_instance, None)
        from_token = 'ETH'
        to_token = 'USDC'
        slippage = 0.99
        amount_to_swap = NativeBalance(10000000, 'ZKSYNC', 'ETH')

        test_dex = MockDex(chain_contracts, tokens, chain_instance, web3, 3, {'from': 1, 'to': 2})

        with self.assertRaises(SwapException):
            test_dex.swap_with_retry(amount_to_swap, from_token, to_token, slippage, zksync_test_account)
