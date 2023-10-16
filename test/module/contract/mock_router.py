from loguru import logger

from sybil_engine.contract.contract import Contract
from sybil_engine.contract.transaction_executor import TransactionExecutionException
from sybil_engine.utils.file_loader import load_abi

abi = load_abi("resources/abi/erc20.json")


class FailMockRouter(Contract):
    def __init__(self, contract_address, web3):
        super().__init__(contract_address, web3, abi)

    def swap(self, account, contract):
        logger.info("swap")
        raise TransactionExecutionException("Error")
