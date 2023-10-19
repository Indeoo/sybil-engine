import functools

from loguru import logger

from sybil_engine.config.app_config import get_dex_retry_interval
from sybil_engine.contract.transaction_executor import TransactionExecutionException, execute_transaction
from sybil_engine.data.contracts import get_contracts_for_chain
from sybil_engine.data.tokens import get_tokens_for_chain
from sybil_engine.domain.balance.balance import NotEnoughERC20Balance
from sybil_engine.domain.balance.tokens import Erc20Token
from sybil_engine.utils.utils import SwapException, randomized_sleeping, AccountException, deprecated


def retry_swap(max_retries=3, exception_type=TransactionExecutionException):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            for retry in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except exception_type as e:
                    if retry == max_retries - 1:  # if it's the last retry
                        raise SwapException(str(e))
                    else:
                        logger.error(str(e))
                        logger.error(f"Error during attempt {retry + 1}/{max_retries}: {e}. Retrying...")
                        randomized_sleeping(self.sleep_interval)
            return None

        return wrapper

    return decorator


class Dex:
    dex_name = None
    swap_contract = None

    def __init__(self, chain_instance, web3, sleep_interval=None):
        self.chain_contracts = get_contracts_for_chain(chain_instance['chain'])
        self.tokens = get_tokens_for_chain(chain_instance['chain'])
        self.chain_instance = chain_instance
        self.web3 = web3

        if sleep_interval is None:
            self.sleep_interval = get_dex_retry_interval()
        else:
            self.sleep_interval = sleep_interval

    @retry_swap(max_retries=3, exception_type=TransactionExecutionException)
    def swap(self, amount_to_swap, from_token, to_token, slippage, account):
        if amount_to_swap.wei == 0 and amount_to_swap.token != self.chain_instance['gas_token']:
            raise NotEnoughERC20Balance(f"Can't swap {amount_to_swap.log_line()}")

        logger.info(f"Swap {amount_to_swap.log_line()}->{to_token} in {self.dex_name} ({self.chain_instance['chain']})")

        from_token_address = self.tokens[from_token]
        to_token_address = self.tokens[to_token]

        if from_token == 'ETH':
            args, func = self.swap_native_for_token(account, amount_to_swap, slippage, to_token_address)
        else:
            erc20_token = Erc20Token(self.chain_instance['chain'], from_token, self.web3)
            balance = erc20_token.balance(account)
            if balance.wei < amount_to_swap.wei:
                raise AccountException(f"Balance {balance.log_line()}<-{amount_to_swap.log_line()}")

            swap_contract = self.chain_contracts[self.swap_contract]

            if erc20_token.allowance(account, swap_contract) < amount_to_swap.wei:
                erc20_token.approve(account, swap_contract)

            if to_token == 'ETH':
                args, func = self.swap_token_for_native(account, amount_to_swap, from_token_address, slippage)
            else:
                args, func = self.swap_token_for_token(account, amount_to_swap, slippage, from_token_address,
                                                       to_token_address)

        if hasattr(func, "__wrapped__"):
            func(*args)
        else:
            execute_transaction(func, args, self.chain_instance, account)

    @deprecated
    def swap_with_retry(self, amount_to_swap, from_token, to_token, slippage, account):
        return self.swap(amount_to_swap, from_token, to_token, slippage, account)

    def swap_token_for_native(self, account, amount_to_swap, from_token_address, slippage):
        raise SwapException("Not supported yet")

    def swap_native_for_token(self, account, amount_to_swap, slippage, to_token_address):
        raise SwapException("Not supported yet")

    def swap_token_for_token(self, account, amount_to_swap, slippage, from_token_address, to_token_address):
        raise SwapException("Not supported yet")

    def get_amount_out_min(self, amount_to_swap, from_token_address, to_token_address):
        raise SwapException("Not supported yet")
