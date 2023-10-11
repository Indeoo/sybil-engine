from loguru import logger

from sybil_engine.config.app_config import get_dex_retry_interval
from sybil_engine.contract.transaction_executor import TransactionExecutionException
from sybil_engine.utils.utils import SwapException, randomized_sleeping


class Dex:
    dex_name = None

    def __init__(self, chain_contracts, tokens, chain_instance, web3, sleep_interval=None):
        self.chain_contracts = chain_contracts
        self.tokens = tokens
        self.chain_instance = chain_instance
        self.web3 = web3
        if sleep_interval is None:
            self.sleep_interval = get_dex_retry_interval()
        else:
            self.sleep_interval = sleep_interval

    def swap(self, amount_to_swap, from_token, to_token, slippage, account):
        raise TransactionExecutionException("Not supported")

    def swap_with_retry(self, amount_to_swap, from_token, to_token, slippage, account, max_retries=3):
        for retry in range(max_retries):
            try:
                return self.swap(amount_to_swap, from_token, to_token, slippage, account)
            except TransactionExecutionException as e:
                if retry == max_retries - 1:  # if it's the last retry
                    raise SwapException(str(e))  # raise the exception to be handled by the calling code
                else:
                    logger.error(str(e))
                    logger.error(f"Error during attempt {retry + 1}/{max_retries}: {e}. Retrying...")
                    randomized_sleeping(self.sleep_interval)
                    continue
        return None
