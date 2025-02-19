import ccxt
from loguru import logger
from okx import Funding, SubAccount
from okx.Account import AccountAPI
from okx.MarketData import MarketAPI
from okx.exceptions import OkxAPIException

from sybil_engine.domain.cex.cex import CEX
from sybil_engine.utils.utils import randomized_sleeping

from sybil_engine.utils.decryptor import read_cex_data

networks = {
    'ETH_MAINNET': 'ERC20',
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


def log(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result is None or result['code'] != '0':
            logger.error(f"Error code: {result['code']} Message: {result['msg']}")
        return result

    return wrapper


class OKX(CEX):
    def __init__(self, cex_data, password):
        self.api_key, self.secret_key, self.passphrase = read_cex_data(cex_data, password)
        self.flag = "0"

    @log
    def withdrawal(self, addr, chain, withdraw_amount, token='ETH'):
        if chain == 'POLYGON' and token == 'USDC':
            network = networks["POLYGON_BRIDGED"]
        else:
            network = networks[chain]

        withdraw_network = token + '-' + network

        fundingAPI = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag, debug=False)

        fee = self._get_withdrawal_fee(token, withdraw_network)
        balance = float(self.get_okx_balance(token)[0]['availBal'])

        if withdraw_amount == balance:
            withdraw_amount = withdraw_amount - fee

        if withdraw_amount > 0:
            return fundingAPI.withdrawal(ccy=token, amt=withdraw_amount, dest=4, toAddr=addr, fee=fee,
                                         chain=withdraw_network)
        else:
            return None

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
        subAccountAPI = SubAccount.SubAccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag,
                                                 debug=False)

        # Get subaccount list
        return subAccountAPI.get_subaccount_list()

    def _transfer_token_from_sub_account(self, acc_name, token):
        amount = self._get_sub_account_balance(acc_name, token)
        if amount > 0:
            logger.info(f"Transfer {amount} {token} from {acc_name} to Main account")
            self._transfer_from_sub_acc(acc_name, amount, token)
            randomized_sleeping({'from': 1, 'to': 1})

    def _get_sub_account_balance(self, acc_name, token):
        subAccountAPI = SubAccount.SubAccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag,
                                                 debug=False)

        return float(subAccountAPI.get_funding_balance(acc_name, token)['data'][0]['bal'])

    def _transfer_from_sub_acc(self, acc_name, amount, token):
        subAccountAPI = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag,
                                           debug=False)

        return subAccountAPI.funds_transfer(token, amount, 6, 6, type='2', subAcct=acc_name)

    def get_okx_deposit_addresses(self):
        fundingAPI = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag, debug=False)
        sub_accounts = fundingAPI.get_deposit_address('ETH')['data']

        return [sub_account['addr'] for sub_account in sub_accounts]

    def get_okx_deposit_address_for_chain(self, chain):
        fundingAPI = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag, debug=False)
        depositAddress = fundingAPI.get_deposit_address('ETH')['data']

        return [addr for addr in depositAddress if addr['chain'] == f'ETH-{networks[chain]}']

    def get_okx_balance(self, currencies):
        fundingAPI = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag, debug=False)

        return fundingAPI.get_balances(currencies)['data']

    def get_total_balance_in_usd(self):
        # Initialize clients – note the separate Funding API for the funding account
        account_client = AccountAPI(
            api_key=self.api_key,
            api_secret_key=self.secret_key,
            passphrase=self.passphrase,
            flag="0",  # 0: Live trading, 1: Demo trading
            debug=False
        )
        market_client = MarketAPI(flag="0")
        funding_client = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag, debug=False)

        try:
            # Get trading account balance (includes details and total equity)
            trading_result = account_client.get_account_balance()
            if trading_result.get('code') != '0':
                print(f"Error fetching trading balance: {trading_result.get('msg')}")
                return None
            trading_data = trading_result.get('data', [{}])[0]
            trading_details = trading_data.get('details', [])

            # Get funding account balance using the Funding API
            # (Note: if FundingAPI is not async, you might need to run it in an executor)
            funding_result = funding_client.get_balances()  # assume async support
            if funding_result.get('code') != '0':
                print(f"Error fetching funding balance: {funding_result.get('msg')}")
                funding_balances = []
            else:
                funding_balances = funding_result.get('data', [])

            # Get tickers to build a price lookup (only SPOT tickers used here)
            tickers_result = market_client.get_tickers('SPOT')
            if tickers_result.get('code') != '0':
                print(f"Error fetching tickers: {tickers_result.get('msg')}")
                return None
            price_lookup = {}
            for ticker in tickers_result.get('data', []):
                symbol = ticker.get('instId', '')
                if symbol.endswith('-USDT') or symbol.endswith('-USDC') or symbol.endswith('-USD'):
                    base_currency = symbol.split('-')[0].upper()
                    price_lookup[base_currency] = float(ticker.get('last', 0))
            # Ensure stablecoins convert 1:1
            for stable in ['USDT', 'USDC', 'USD', 'DAI', 'BUSD']:
                price_lookup[stable] = 1.0

            total_usd_value = 0.0
            assets_details = []

            # Process trading account assets
            for asset in trading_details:
                currency = asset.get('ccy', '').upper()
                # For trading account, OKX uses cashBal to indicate available balance
                balance = float(asset.get('cashBal', 0))
                if balance > 0:
                    # Try price lookup; if not found, attempt alternative key
                    usd_value = balance * (price_lookup.get(currency) or price_lookup.get(f"{currency}-USDT") or 0)
                    assets_details.append({
                        'currency': currency,
                        'balance': balance,
                        'usd_value': usd_value,
                        'account': 'Trading'
                    })
                    total_usd_value += usd_value

            # Process funding account assets
            for asset in funding_balances:
                currency = asset.get('ccy', '').upper()
                available = float(asset.get('availBal', 0))
                frozen = float(asset.get('frozenBal', 0))
                balance = available + frozen
                if balance > 0:
                    usd_value = balance * (price_lookup.get(currency) or price_lookup.get(f"{currency}-USDT") or 0)
                    assets_details.append({
                        'currency': currency,
                        'balance': balance,
                        'usd_value': usd_value,
                        'account': 'Funding'
                    })
                    total_usd_value += usd_value

            # Use the reported total equity from the trading account (if desired)
            reported_total = float(trading_data.get('totalEq', '0'))

            return {
                'calculated_total_usd': total_usd_value,
                'reported_total_usd': reported_total,
                'assets': sorted(assets_details, key=lambda x: x['usd_value'], reverse=True)
            }

        except OkxAPIException as e:
            print(f"API Error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
