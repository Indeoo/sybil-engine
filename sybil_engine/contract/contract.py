class Contract:

    def __init__(self, contract_address, web3, abi=None):
        self.contract_address = contract_address
        self.web3 = web3
        if abi is not None:
            self.contract = web3.eth.contract(address=contract_address, abi=abi)

    def build_generic_data(self, sender):
        return {
            "chainId": self.web3.eth.chain_id,
            'from': sender,
            'to': self.contract_address,
            'nonce': self.web3.eth.get_transaction_count(sender),
            'gasPrice': self.web3.eth.gas_price,
        }

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