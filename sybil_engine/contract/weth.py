from sybil_engine.contract.contract import Contract
from sybil_engine.utils.file_loader import load_abi

abi = load_abi("resources/abi/weth.json")


class WETH(Contract):
    def __init__(self, contract_address, web3):
        super().__init__(contract_address, web3, abi)

    def deposit(self, amount_to_swap, account):
        sender = account.address

        txn_params = self.build_generic_data(sender)
        txn_params['value'] = amount_to_swap.wei
        txn_params['data'] = self.contract.encodeABI("deposit")

        return txn_params

    def withdraw(self, amount_to_swap, account):
        sender = account.address

        txn_params = self.build_generic_data(sender)
        txn_params['data'] = self.contract.encodeABI("withdraw", args=(amount_to_swap.wei,))

        return txn_params

    def balance_of(self, account):
        return self.contract.functions.balanceOf(account.address).call()
