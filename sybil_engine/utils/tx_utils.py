from sybil_engine.utils.utils import AppException

from sybil_engine.utils.retry import retry


@retry(max_attempts=3, retry_interval={'from': 60 * 1, 'to': 60 * 4})
def wait_for_transaction(tx_hash, web3):
    web3.eth.wait_for_transaction_receipt(tx_hash)


class TransactionExecutionException(AppException):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)