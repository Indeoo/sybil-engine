from sybil_engine.domain.dex import Dex
from loguru import logger

from test.module.contract.mock_router import FailMockRouter


class MockFailDex(Dex):
    dex_name = 'MockDex'
    swap_contract = 'USDC'

    def __init__(self, chain_instance, web3, retries, sleeping_interval, retry_counter=0):
        self.reties = retries
        self.retry_counter = retry_counter
        super().__init__(chain_instance, web3, sleeping_interval)
        self.erc20_contract = FailMockRouter(self.tokens[self.swap_contract], self.web3)

    def swap(self, amount_to_swap, from_token, to_token, slippage, account):
        if self.retry_counter < self.reties:
            self.retry_counter += 1
            super().swap(amount_to_swap, from_token, to_token, slippage, account)

    def swap_token_for_native(self, account, amount_to_swap, from_token_address, slippage):
        logger.info("swap_token_for_native")

        return [account, '0x80115c708E12eDd42E504c1cD52Aea96C547c05c'], self.erc20_contract.swap

    def swap_token_for_token(self, account, amount_to_swap, slippage, from_token_address, to_token_address):
        logger.info("swap_token_for_token")

        return [account, '0x80115c708E12eDd42E504c1cD52Aea96C547c05c'], self.erc20_contract.swap

    def swap_native_for_token(self, account, amount_to_swap, slippage, to_token_address):
        logger.info("swap_native_for_token")

        return [account, '0x80115c708E12eDd42E504c1cD52Aea96C547c05c'], self.erc20_contract.swap
