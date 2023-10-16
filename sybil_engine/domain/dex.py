from loguru import logger

from sybil_engine.config.app_config import get_dex_retry_interval
from sybil_engine.contract.transaction_executor import TransactionExecutionException, execute_transaction
from sybil_engine.domain.balance.tokens import Erc20Token
from sybil_engine.utils.utils import SwapException, randomized_sleeping, AccountException


class Dex:
    dex_name = None
    swap_contract = None

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
        from_token_address = self.tokens[from_token]
        to_token_address = self.tokens[to_token]

        if from_token == 'ETH':
            args, func = self.swap_native_for_token(account, amount_to_swap, slippage, to_token_address)
        else:
            erc20_token = Erc20Token(self.chain_instance['chain'], from_token, self.web3)
            balance = erc20_token.balance(account)
            if balance.wei < amount_to_swap.wei:
                raise AccountException(f"Balance {balance.log_line()} < {amount_to_swap.log_line()}")

            swap_contract = self.chain_contracts[self.swap_contract]

            if erc20_token.allowance(account, swap_contract) < amount_to_swap.wei:
                execute_transaction(erc20_token.approve, [account, swap_contract], self.chain_instance, account,
                                    self.web3)

            if to_token == 'ETH':
                args, func = self.swap_token_for_native(account, amount_to_swap, from_token_address, slippage)
            else:
                func, args = self.swap_token_for_token()

        execute_transaction(func, args, self.chain_instance, account, self.web3)

    def swap_token_for_native(self, account, amount_to_swap, from_token_address, slippage):
        raise Exception("Not supported yet")

    def swap_native_for_token(self, account, amount_to_swap, slippage, to_token_address):
        raise Exception("Not supported yet")

    def swap_token_for_token(self, account, amount_to_swap, slippage, from_token_address, to_token_address):
        raise Exception("Not supported yet")

    def get_amount_out_min(self, amount_to_swap, from_token_address, to_token_address):
        raise Exception("Not supported yet")

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
