import functools

from loguru import logger
from web3 import Web3

from sybil_engine.config.app_config import get_gas_prices
from sybil_engine.domain.balance.balance_utils import from_wei_to_gwei
from sybil_engine.utils.utils import randomized_sleeping

web3_main = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))


def check_gas_price(chain_instance, web3):
    while True:
        try:
            return verify_gas_price(chain_instance, web3)
        except GasPriceToHigh as e:
            logger.info(e)
            randomized_sleeping({'from': 60 * 4, 'to': 60 * 8})


def verify_gas_price(chain_instance, web3):
    gas_price_wei = web3.eth.gas_price

    verify_l2_gas_price(chain_instance, gas_price_wei)
    verify_l1_gas_price()

    return gas_price_wei


def verify_l2_gas_price(chain_instance, gas_price_wei):
    zksync_max_gas_price = chain_instance['gas_price_gwei']
    if from_wei_to_gwei(gas_price_wei) > zksync_max_gas_price:
        raise GasPriceToHigh(
            f"Gas price is to high: {from_wei_to_gwei(gas_price_wei)}Gwei, max: {zksync_max_gas_price}Gwei")


def l1_gas_price(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        check_l1_gas_price()

        return func(*args, **kwargs)
    return wrapper


def check_l1_gas_price():
    while True:
        try:
            return verify_l1_gas_price()
        except GasPriceToHigh as e:
            logger.info(e)
            randomized_sleeping({'from': 60 * 4, 'to': 60 * 8})


def verify_l1_gas_price():
    l1_max_gas_price = get_gas_prices()['ETH_MAINNET']
    l1_gas_price_wei = web3_main.eth.gas_price

    if from_wei_to_gwei(l1_gas_price_wei) > l1_max_gas_price:
        raise GasPriceToHigh(
            f"L1 Gas price is to high: {from_wei_to_gwei(l1_gas_price_wei)}Gwei, max: {l1_max_gas_price}Gwei")


class GasPriceToHigh(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
