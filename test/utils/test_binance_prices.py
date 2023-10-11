
import logging
import unittest

from sybil_engine.domain.balance.balance import NativeBalance, Erc20Balance
from sybil_engine.utils.binance_prices import get_amount_out_from_eth, get_amount_out_to_eth


# todo: finish tests
class TestBinancePrices(unittest.TestCase):

    def test_get_amount_out_from_eth(self):
        balance = NativeBalance(1000000000000000000, 'ZKSYNC', 'ETH')

        logging.info(f"Amount out from eth {get_amount_out_from_eth(balance, 'ETH', 'USDC', 0.98)}")

    def test_get_amount_out_to_eth(self):
        balance = Erc20Balance(1000000, 'ZKSYNC', 'USDC')

        logging.info(f"Amount out to eth {get_amount_out_to_eth(balance, 'USDC', 'ETH', 0.98)}")
