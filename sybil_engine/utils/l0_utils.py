from loguru import logger
from sybil_engine.domain.balance.balance import NotEnoughNativeBalance, NativeBalance
from sybil_engine.domain.balance.balance_utils import from_eth_to_wei


def verify_stargate_l0_price(account, chain_instance, to_chain_instance, native_balance, stargate_router):
    native_fee_balance = NativeBalance(
        stargate_router.count_native_fee_stargate(
            to_chain_instance['stargate_chain_id'],
            account.address
        ),
        native_balance.token,
        native_balance.chain
    )

    logger.info(f"Native LayerZero fee: {native_fee_balance.log_line()}")
    if native_fee_balance.wei > native_balance.wei:
        raise NotEnoughNativeBalance(
            f"Native balance ({native_balance.log_line()}) < Native LayerZero required fee")
    if native_fee_balance.wei > from_eth_to_wei(chain_instance['max_l0_fee']):
        raise NativeFeeToHigh(f"Native LayerZero fee is to high")


def verify_stargate_eth_l0_price(from_chain_instance, to_chain_instance, native_balance, layer_zero,
                                 stargate_router_eth):
    native_fee_balance = NativeBalance(
        layer_zero.count_native_fee_swap_eth(
            stargate_router_eth,
            to_chain_instance
        ),
        native_balance.token,
        native_balance.chain
    )

    logger.info(f"Native LayerZero fee: {native_fee_balance.log_line()}")
    if native_fee_balance.wei > native_balance.wei:
        raise NotEnoughNativeBalance(
            f"Native balance ({native_balance.log_line()}) < Native LayerZero required fee")
    if native_fee_balance.wei > from_eth_to_wei(from_chain_instance['max_l0_fee']):
        raise NativeFeeToHigh(f"Native LayerZero fee is to high")


class NativeFeeToHigh(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
