from loguru import logger

from sybil_engine.domain.balance.balance_utils import from_wei_to_eth
from sybil_engine.utils.binance_prices import get_binance_price

FEE = {
    'ETH': 0,
    'MATIC': 0,
    'BNB': 0,
    'AVAX': 0,
    'FTM': 0
}


def add_fee(gas_token, transaction_price_wei):
    FEE[gas_token] += transaction_price_wei


def print_fee():
    converted_dict = {k: float(from_wei_to_eth(v)) for k, v in FEE.items()}

    amount = 0
    for token, fee in FEE.items():
        price = get_binance_price(token + 'USDT')
        amount = amount + float(from_wei_to_eth(fee)) * price

    logger.info(f"Total fee is: {converted_dict}")
    logger.info(f"Approximate USD cost: {amount}")
