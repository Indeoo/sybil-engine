import random

import ccxt
from loguru import logger
from okx import Funding, SubAccount

from sybil_engine.utils.decryptor import decrypt_okx_api

networks = {
    'ZKSYNC': 'zkSync Era',
    'LINEA': 'Linea'
}
symbolWithdraw = 'ETH'


def get_withdrawal_fee(api_key, secret_key, passphrase, symbol_withdraw, chain_name):
    exchange = ccxt.okx({
        'apiKey': api_key,
        'secret': secret_key,
        'password': passphrase,
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


def withdrawal(addr, password, chain, cex_data, withdraw_interval):
    api_key, secret_key, passphrase = decrypt_okx_api(cex_data, password).split(',')
    flag = "0"
    withdraw_network = symbolWithdraw + '-' + networks[chain]

    fundingAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)

    fee = get_withdrawal_fee(api_key, secret_key, passphrase, 'ETH', withdraw_network)

    amount = round(random.uniform(withdraw_interval['from'], withdraw_interval['to']), 6)

    print(f"Withdraw ETH {amount}ETH")

    fundingAPI.withdrawal(ccy='ETH', amt=amount, dest=4, toAddr=addr, fee=fee, chain=withdraw_network)


def get_sub_accounts(cex_data, password):
    api_key, secret_key, passphrase = decrypt_okx_api(cex_data, password).split(',')

    flag = "0"  # Production trading: 0, Demo trading: 1

    subAccountAPI = SubAccount.SubAccountAPI(api_key, secret_key, passphrase, False, flag, debug=False)

    # Get sub-account list
    return subAccountAPI.get_subaccount_list()


def get_sub_account_balance(acc_name, token, cex_data, password):
    api_key, secret_key, passphrase = decrypt_okx_api(cex_data, password).split(',')

    flag = "0"

    subAccountAPI = SubAccount.SubAccountAPI(api_key, secret_key, passphrase, False, flag, debug=False)

    return float(subAccountAPI.get_funding_balance(acc_name, token)['data'][0]['bal'])


def transfer_from_sub_acc(acc_name, amount, token, cex_data, password):
    api_key, secret_key, passphrase = decrypt_okx_api(cex_data, password).split(',')

    flag = "0"

    subAccountAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag, debug=False)

    return subAccountAPI.funds_transfer(token, amount, 6, 6, type='2', subAcct=acc_name)


def okx_transfer_from_sub_account(okx_secret, cex_data):
    for acc in get_sub_accounts(cex_data, okx_secret)['data']:
        token = 'ETH'
        acc_name = acc['subAcct']

        amount = get_sub_account_balance(acc_name, token, cex_data, okx_secret)

        if amount > 0:
            logger.info(f"Transfer {amount} {token} from {acc_name} to Main account")
            transfer_from_sub_acc(acc_name, amount, token, cex_data, okx_secret)
        else:
            logger.info(f"{acc_name} is empty, no transfer required")
