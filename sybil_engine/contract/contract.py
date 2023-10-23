from sybil_engine.data.networks import ids_chain, get_chain_instance


class Contract:

    def __init__(self, contract_address, web3, abi=None):
        self.contract_address = contract_address
        self.web3 = web3
        self.chain_instance = get_chain_instance(ids_chain[web3.eth.chain_id])
        if abi is not None:
            self.contract = web3.eth.contract(address=contract_address, abi=abi)

    def build_generic_data(self, sender, set_contract_address=True):
        txn_data = {
            "chainId": self.web3.eth.chain_id,
            'from': sender,
            'nonce': self.web3.eth.get_transaction_count(sender),
            'gasPrice': self.web3.eth.gas_price,
        }

        if set_contract_address:
            txn_data['to'] = self.contract_address

        return txn_data

    def build_txn_params(self, from_chain_instance, from_address, gas_price_wei):
        nonce = self.web3.eth.get_transaction_count(from_address)

        if from_chain_instance['eip1599']:
            latest_block = self.web3.eth.get_block('latest')
            base_fee_per_gas = latest_block['baseFeePerGas']
            return {
                'from': from_address,
                'nonce': nonce,
                'gas': 10000000,
                'maxFeePerGas': int(base_fee_per_gas * 1.6),
            }
        else:
            return {
                'from': from_address,
                'nonce': nonce,
                'gas': 15000000,
                'gasPrice': gas_price_wei
            }

    def get_gas_price(self, chain):
        if chain == 'AVALANCHE' or chain == 'POLYGON':
            latest_block = self.web3.eth.get_block('latest')
            base_fee_per_gas = latest_block['baseFeePerGas']
            return int(base_fee_per_gas * 1.8)
        else:
            return self.web3.eth.gas_price
