from loguru import logger
from web3 import Web3

from sybil_engine.utils.fee_storage import add_fee
from sybil_engine.utils.gas_utils import verify_gas_price, GasPriceToHigh
from sybil_engine.utils.l0_utils import NativeFeeToHigh
from sybil_engine.utils.opti_utils import wait_for_optimism
from sybil_engine.utils.utils import randomized_sleeping


def execute_transaction(func, args, chain_instance, account, web3):
    while True:
        try:
            gas_price_wei = verify_gas_price(chain_instance, web3)
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

            transaction_price_wei = tx_receipt['gasUsed'] * gas_price_wei
            logger.info(f"Transaction fee: {from_wei_to_eth(transaction_price_wei)} {chain_instance['gas_token']}")

            add_fee(chain_instance['gas_token'], transaction_price_wei)
            return tx_hash

        except GasPriceToHigh as e:
            logger.info(e)
            randomized_sleeping({'from': 60 * 4, 'to': 60 * 8})
        except Exception as e:
            raise TransactionExecutionException(e)


def execute_starknet_bridge_transaction(func, args, chain_instance, account, web3):
    while True:
        try:
            tx_hash = execute_transaction(func, args, chain_instance, account, web3)

            logger.info(f'>>> https://starkscan.co/contract/{account.starknet_address}#token-transfers')

            return tx_hash
        except NativeFeeToHigh as e:
            logger.info(e)
            randomized_sleeping({'from': 60 * 4, 'to': 60 * 8})


class TransactionExecutionException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
