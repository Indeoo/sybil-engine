from sybil_engine.contract.contract import Contract
from sybil_engine.contract.transaction_executor import evm_transaction
from web3 import Web3


class Send(Contract):

    @evm_transaction
    def send_to_wallet(self, account, to_address, amount_to_swap):
        sender = Web3.to_checksum_address(account.address)

        txn_params = self.build_generic_data(sender, False)
        txn_params['value'] = amount_to_swap.wei
        txn_params['gasPrice'] = self.web3.eth.gas_price
        txn_params['to'] = Web3.to_checksum_address(to_address)

        return txn_params
