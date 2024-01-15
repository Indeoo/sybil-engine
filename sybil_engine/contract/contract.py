from sybil_engine.data.networks import ids_chain, get_chain_instance


class Contract:

    def __init__(self, contract_address, web3, abi=None):
        self.contract_address = contract_address
        self.web3 = web3
        self.chain_instance = get_chain_instance(ids_chain[web3.eth.chain_id])
        if abi is not None:
            self.contract = web3.eth.contract(address=contract_address, abi=abi)

    def build_generic_data(self, sender, set_contract_address=True, eip_1599=False):
        txn_data = {
            "chainId": self.web3.eth.chain_id,
            'from': sender,
            'nonce': self.web3.eth.get_transaction_count(sender),
        }

        self.set_gas(eip_1599, txn_data)

        if set_contract_address:
            txn_data['to'] = self.contract_address

        return txn_data

    def set_gas(self, eip_1599, txn_data):
        if eip_1599:
            txn_data['maxFeePerGas'] = int(self.get_base_fee_per_gas() * 1.125 ** 3)
        else:
            txn_data['gasPrice'] = self.web3.eth.gas_price

    def get_base_fee_per_gas(self):
        latest_block = self.web3.eth.get_block('latest')
        return latest_block['baseFeePerGas']
