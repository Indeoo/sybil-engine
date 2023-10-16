import unittest

from loguru import logger
from sybil_engine.data.contracts import get_contracts_for_chain
from sybil_engine.data.networks import get_chain_instance
from sybil_engine.data.pairs import Pairs
from sybil_engine.data.tokens import get_tokens_for_chain
from sybil_engine.utils.web3_utils import init_web3
from test import init_set_test_config
from test.module.swap.mock_test_swap_facade import swap_facade


class TestSwapFacade(unittest.TestCase):
    init_set_test_config()

    def test_shouldGetDex(self):
        logger.info("Test swap facade")

        chain_contracts = get_contracts_for_chain("ZKSYNC")
        tokens = get_tokens_for_chain('ZKSYNC')
        dex_apps = swap_facade.get_swap_apps_by_chain('ZKSYNC')
        chain_instance = get_chain_instance('ZKSYNC')
        pairs = Pairs(swap_facade).get_pairs_by_tokens('ETH', 'USDC', 'ZKSYNC')
        web3 = init_web3(chain_instance, None)

        try:
            for swap_app in dex_apps:
                for pair in pairs:
                    print(swap_facade.get_dex(chain_contracts, pair, swap_app, tokens, chain_instance, web3))
        except Exception as e:
            self.fail(f"Some function raised an exception: {e}")
