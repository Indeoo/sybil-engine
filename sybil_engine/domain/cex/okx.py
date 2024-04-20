import ccxt
from loguru import logger
from okx import Funding, SubAccount

from sybil_engine.domain.cex import CEX
from sybil_engine.utils.utils import randomized_sleeping

from sybil_engine.utils.decryptor import read_cex_data

networks = {
    'ZKSYNC': 'zkSync Era',
    'LINEA': 'Linea',
    'ARBITRUM': 'Arbitrum One',
    'BASE': 'Base',
    'POLYGON': 'Polygon',
    'POLYGON_BRIDGED': 'Polygon (Bridged)',
    'COREDAO': 'CORE',
    'OPTIMISM': 'Optimism',
    'X_LAYER': 'X Layer'
}


class OKX(CEX):
    def __init__(self, cex_data, password):
        self.api_key, self.secret_key, self.passphrase = read_cex_data(cex_data, password)

    def withdrawal(self, addr, chain, withdraw_amount, token='ETH'):
        flag = "0"

        if chain == 'POLYGON' and token == 'USDC':
            network = networks["POLYGON_BRIDGED"]
        else:
            network = networks[chain]

        withdraw_network = token + '-' + network

        fundingAPI = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, flag, debug=False)

        fee = self._get_withdrawal_fee(token, withdraw_network)

        fundingAPI.withdrawal(ccy=token, amt=withdraw_amount, dest=4, toAddr=addr, fee=fee, chain=withdraw_network)

    def _get_withdrawal_fee(self, symbol_withdraw, chain_name):
        exchange = ccxt.okx({
            'apiKey': self.api_key,
            'secret': self.secret_key,
            'password': self.passphrase,
            'enableRateLimit': True
        })

        currencies = exchange.fetch_currencies()
        for currency in currencies:
            if currency == symbol_withdraw:
                currency_info = currencies[currency]
                network_info = currency_info.get('networks', None)
                if network_info:
                    for network in network_info:
                        network_data = network_info[network]
                        network_id = network_data['id']
                        if network_id == chain_name:
                            withdrawal_fee = currency_info['networks'][network]['fee']
                            if withdrawal_fee == 0:
                                return 0
                            else:
                                return withdrawal_fee

        raise ValueError(f"     не могу получить сумму комиссии, проверьте значения symbolWithdraw и network")

    def transfer_from_sub_account(self, tokens=['ETH']):
        for acc in self._get_sub_accounts()['data']:
            for token in tokens:
                self._transfer_token_from_sub_account(acc['subAcct'], token)

    def _get_sub_accounts(self):
        flag = "0"  # Production trading: 0, Demo trading: 1

        subAccountAPI = SubAccount.SubAccountAPI(self.api_key, self.secret_key, self.passphrase, False, flag, debug=False)

        # Get subaccount list
        return subAccountAPI.get_subaccount_list()

    def _transfer_token_from_sub_account(self, acc_name, token):
        amount = self._get_sub_account_balance(acc_name, token)
        if amount > 0:
            logger.info(f"Transfer {amount} {token} from {acc_name} to Main account")
            self._transfer_from_sub_acc(acc_name, amount, token)
            randomized_sleeping({'from': 1, 'to': 1})

    def _get_sub_account_balance(self, acc_name, token):
        flag = "0"

        subAccountAPI = SubAccount.SubAccountAPI(self.api_key, self.secret_key, self.passphrase, False, flag, debug=False)

        return float(subAccountAPI.get_funding_balance(acc_name, token)['data'][0]['bal'])

    def _transfer_from_sub_acc(self, acc_name, amount, token):
        flag = "0"

        subAccountAPI = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, flag, debug=False)

        return subAccountAPI.funds_transfer(token, amount, 6, 6, type='2', subAcct=acc_name)

    def get_okx_deposit_addresses(self):
        flag = "0"

        subAccountAPI = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, flag, debug=False)
        sub_accounts = subAccountAPI.get_deposit_address('ETH')['data']

        return [sub_account['addr'] for sub_account in sub_accounts]
