from sybil_engine.domain.dex import Dex


class MockDex(Dex):
    def __init__(self, chain_instance, web3, retries, sleeping_interval, retry_counter=0):
        self.reties = retries
        self.retry_counter = retry_counter
        super().__init__(chain_instance, web3, sleeping_interval)

    def swap(self, amount_to_swap, from_token, to_token, slippage, account):
        if self.retry_counter < self.reties:
            self.retry_counter += 1
            super().swap(amount_to_swap, from_token, to_token, slippage, account)

