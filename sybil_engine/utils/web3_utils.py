import random
from typing import Optional, Any

from loguru import logger
from web3 import Web3
from web3.middleware import geth_poa_middleware

from sybil_engine.data.networks import get_chain_instance
from sybil_engine.domain.balance.balance_utils import get_native_balance, find_chain_with_max_usdc, \
    find_chain_with_max_native
from sybil_engine.domain.balance.tokens import Erc20Token


def init_web3(chain_instance, proxy: Optional[Any]):
    if proxy is not None:
        provider = Web3.HTTPProvider(chain_instance['rpc'], request_kwargs={"proxies": {'https': proxy, 'http': proxy}})
    else:
        provider = Web3.HTTPProvider(endpoint_uri=chain_instance['rpc'])

    web3 = Web3(provider=provider)

    if chain_instance['poa']:
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    return web3


def get_amount_to_bridge_usdc(bridge_amount_interval):
    if bridge_amount_interval['from'] > bridge_amount_interval['to']:
        raise Exception('Invalid bridge interval')

    return int(
        random.randint(bridge_amount_interval['from'] * 10 ** 2, bridge_amount_interval['to'] * 10 ** 2)) * 10 ** 4


def print_account_data(account_data):
    for chain, usdc, native_balance, web3 in account_data:
        logger.info(f"{chain}: {usdc.log_line()}, {native_balance.log_line()}")


def get_all_account_data(account, chains):
    balances = []
    for chain in chains:
        web3 = init_web3(get_chain_instance(chain), account.proxy)
        native_balance = get_native_balance(account, web3, get_chain_instance(chain))

        erc20_from_token = Erc20Token(chain, 'USDC', web3)

        erc20_balance = erc20_from_token.balance(account)

        balances = balances + [(chain, erc20_balance, native_balance, web3)]

    return balances


def get_max_balance_data(token_type, chains, account):
    data = get_all_account_data(account, chains)
    print_account_data(data)

    if token_type == 'USDC':
        return find_chain_with_max_usdc(data)
    else:
        return find_chain_with_max_native(data)