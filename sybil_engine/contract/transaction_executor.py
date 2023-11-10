from loguru import logger
from web3 import Web3

from sybil_engine.domain.balance.balance_utils import from_wei_to_eth
from sybil_engine.utils.fee_storage import add_fee
from sybil_engine.utils.gas_utils import check_gas_price
from sybil_engine.utils.l0_utils import NativeFeeToHigh
from sybil_engine.utils.opti_utils import wait_for_optimism
from sybil_engine.utils.utils import randomized_sleeping, deprecated

from functools import wraps


def evm_transaction(func):
    @wraps(func)
    def wrapper(instance, account, *args):
        chain_instance = instance.chain_instance
        web3 = instance.web3
        args = instance, account, * args

        return execute_transaction_internal(func, args, chain_instance, account, web3)
    return wrapper


@deprecated
def execute_transaction(func, args, chain_instance, account, web3=None):
    return execute_transaction_internal(func, args, chain_instance, account, web3)


def execute_transaction_internal(func, args, chain_instance, account, web3=None):
    if web3 is None:
        web3 = func.__self__.web3

    gas_price_wei = check_gas_price(chain_instance, web3)

    try:
        contract_txn = func(*args)

        if 'gas' not in contract_txn:
            contract_txn['gas'] = web3.eth.estimate_gas(contract_txn)

        signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=account.key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        randomized_sleeping(chain_instance['transaction_sleep_interval'])

        wait_for_optimism(chain_instance)

        web3.eth.wait_for_transaction_receipt(tx_hash)

        logger.info(f">>> {chain_instance['scan']}/{Web3.to_hex(tx_hash)}")
        tx_receipt = web3.eth.get_transaction_receipt(tx_hash)

        transaction_status = tx_receipt['status']
        if transaction_status == 0:
            raise TransactionExecutionException("Transaction failed.")
    except Exception as e:
        raise TransactionExecutionException("Transaction failed.") from e

    transaction_price_wei = tx_receipt['gasUsed'] * gas_price_wei
    logger.info(f"Transaction fee: {from_wei_to_eth(transaction_price_wei)} {chain_instance['gas_token']}")

    add_fee(chain_instance['gas_token'], transaction_price_wei)

    return tx_hash


def evm_starknet_transaction(func):
    @wraps(func)
    def wrapper(instance, account, *args):
        chain_instance = instance.chain_instance
        web3 = instance.web3
        args = instance, account, * args

        return execute_starknet_bridge_transaction_internal(func, args, chain_instance, account, web3)
    return wrapper


@deprecated
def execute_starknet_bridge_transaction(func, args, chain_instance, account, web3):
    return execute_starknet_bridge_transaction_internal(account, args, chain_instance, func, web3)


def execute_starknet_bridge_transaction_internal(account, args, chain_instance, func, web3):
    while True:
        try:
            tx_hash = execute_transaction_internal(func, args, chain_instance, account, web3)

            logger.info(f'>>> https://starkscan.co/contract/{account.starknet_address}#token-transfers')

            return tx_hash
        except NativeFeeToHigh as e:
            logger.info(e)
            randomized_sleeping({'from': 60 * 4, 'to': 60 * 8})


class TransactionExecutionException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
