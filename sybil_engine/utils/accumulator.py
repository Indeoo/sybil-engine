from loguru import logger

from sybil_engine.domain.balance.balance import Erc20Balance

accumulator = {
}


def add_accumulator(key: str, value: int):
    if key not in accumulator:
        accumulator[key] = value

    accumulator[key] += value


def add_accumulator_balance(key: str, value: int):
    if key not in accumulator:
        accumulator[key] = Erc20Balance(0, None, 'USDC')

    accumulator[key] = Erc20Balance(accumulator[key].wei + value, None, 'USDC')


def add_accumulator_str(key: str, value: str):
    if key not in accumulator:
        accumulator[key] = []

    accumulator[key].append(value)


def get_value(key: str):
    return accumulator.get(key)


def print_accumulated():
    for key, value in accumulator.items():
        logger.info(f"{key}: {value}")
