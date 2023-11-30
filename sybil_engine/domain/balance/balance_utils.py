from loguru import logger
from web3 import Web3

from sybil_engine.config.app_config import get_okx
from sybil_engine.domain.balance.balance import NotEnoughNativeBalance, Erc20Balance, WETHBalance, NativeBalance
from sybil_engine.utils.utils import interval_to_round, deprecated


def from_wei_to_eth(wei):
    return Web3().from_wei(wei, 'ether')


def from_wei_to_gwei(wei):
    return Web3().from_wei(wei, 'gwei')


def from_eth_to_wei(eth):
    return Web3().to_wei(eth, 'ether')


def verify_balance(min_native_balance, chain_instance, account, web3):
    native_balance = get_native_balance(account, web3, chain_instance)

    logger.info(f"Native balance: {native_balance.log_line()}")

    _, (_, auto_withdrawal, min_auto_withdraw_interval, _) = get_okx()

    if min_native_balance.wei >= native_balance.wei:
        raise NotEnoughNativeBalance(f"Min native balance {min_native_balance.log_line()} > native balance",
                                     chain_instance['chain'])

    if auto_withdrawal:
        min_auto_withdrawal_balance = interval_to_eth_balance(min_auto_withdraw_interval, account, chain_instance['chain'], web3)
        if min_auto_withdrawal_balance.wei >= native_balance.wei:
            raise NotEnoughNativeBalance(f"Min balance for OKX {min_auto_withdrawal_balance.log_line()} > native balance",
                                         chain_instance['chain'])

    return native_balance.minus(min_native_balance)


def amount_to_swap_for_pair(account, chain, min_native_balance, native_balance, pair, swap_amount_interval, swap_token,
                            web3):
    if swap_amount_interval == '':
        swap_amount_interval = pair['amount']

    if swap_token == 'ETH':
        amount_to_swap = interval_to_eth_balance(swap_amount_interval, account, chain, web3)

        if swap_amount_interval == 'all_balance':
            amount_to_swap = amount_to_swap.minus(min_native_balance)

        if amount_to_swap.wei > native_balance.wei:
            raise NotEnoughNativeBalance(
                f"Account balance {native_balance.log_line()} < {amount_to_swap.log_line()} amount to swap.")
    else:
        amount_to_swap = interval_to_erc20_balance(swap_amount_interval, account, swap_token, chain, web3)

    return amount_to_swap


def interval_to_erc20_balance(erc20_interval, account, token, chain, web3):
    from sybil_engine.domain.balance.tokens import Erc20Token

    erc20_balance = Erc20Token(chain, token, web3).balance(account)

    if erc20_interval == 'all_balance':
        return erc20_balance
    else:
        return Erc20Balance(int(interval_to_round(erc20_interval) * 10 ** erc20_balance.decimal), chain, token)


def interval_to_weth_balance(erc20_interval, account, chain, web3):
    from sybil_engine.domain.balance.tokens import WETHToken

    if erc20_interval == 'all_balance':
        return WETHToken(chain, web3).balance(account)
    else:
        return WETHBalance(int(interval_to_round(erc20_interval) * 10 ** 6), chain)


def interval_to_eth_balance(eth_interval, account, chain, web3):
    if eth_interval == 'all_balance':
        balance = get_native_balance_for_params(account, web3, chain, 'ETH')
    else:
        balance = NativeBalance(from_eth_to_wei(interval_to_round(eth_interval)), chain, 'ETH')

    return NativeBalance(int(balance.wei // 10000) * 10000, chain, balance.token)


def get_native_balance(account, web3, chain_instance):
    return NativeBalance(web3.eth.get_balance(account.address), chain_instance['chain'], chain_instance['gas_token'])


def get_native_balance_for_params(account, web3, chain, token):
    return NativeBalance(web3.eth.get_balance(account.address), chain, token)


def find_chain_with_max_usdc(account_data):
    max_usdc_balance = max(account_data, key=lambda x: x[1].wei_compare())

    if max_usdc_balance[1] == 0:
        raise Exception("Can't bridge tokens, all chain USDC balances are zero")

    return max_usdc_balance


def find_chain_with_max_native(account_data):
    max_native_balance = max(account_data, key=lambda x: x[2].wei_compare())

    if max_native_balance[2] == 0:
        raise Exception("Can't bridge tokens, all chain ETH balances are zero")

    return max_native_balance
