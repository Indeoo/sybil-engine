from web3 import Web3

from sybil_engine.domain.balance.balance_utils import from_wei_to_gwei

web3_main = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))


def verify_gas_price(chain_instance, web3):
    gas_price_wei = web3.eth.gas_price
    l1_gas_price_wei = web3_main.eth.gas_price

    l1_max_gas_price = chain_instance['l1_gas_price_gwei']
    zksync_max_gas_price = chain_instance['gas_price_gwei']

    if from_wei_to_gwei(l1_gas_price_wei) > l1_max_gas_price:
        raise GasPriceToHigh(
            f"L1 Gas price is to high: {from_wei_to_gwei(l1_gas_price_wei)}Gwei, max: {l1_max_gas_price}Gwei")

    if from_wei_to_gwei(gas_price_wei) > zksync_max_gas_price:
        raise GasPriceToHigh(
            f"Gas price is to high: {from_wei_to_gwei(gas_price_wei)}Gwei, max: {zksync_max_gas_price}Gwei")

    return gas_price_wei


class GasPriceToHigh(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)