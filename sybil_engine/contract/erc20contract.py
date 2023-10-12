from loguru import logger
from web3 import Web3

from sybil_engine.contract.contract import Contract
from sybil_engine.utils.file_loader import load_abi

abi = load_abi("resources/abi/erc20.json")

MAX_ALLOWANCE = 115792089237316195423570985008687907853269984665640564039457584007913129639935


class Erc20Contract(Contract):
    def __init__(self, contract_address, web3):
        super().__init__(contract_address, web3, abi)

    def approve(self, account, contract_on_approve):
        logger.info(f"Approving token")

        txn_params = self.build_generic_data(account.address)

        del txn_params['to']
        return self.contract.functions.approve(
            Web3.to_checksum_address(contract_on_approve),
            MAX_ALLOWANCE
        ).build_transaction(txn_params)

    def balance_of(self, account):
        return self.contract.functions.balanceOf(account.address).call()

    def allowance(self, account, allowance_contract):
        return self.contract.functions.allowance(account.address, Web3.to_checksum_address(allowance_contract)).call()
