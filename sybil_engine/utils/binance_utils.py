from binance.error import ClientError
from binance.spot import Spot

from sybil_engine.utils.decryptor import decrypt_cex_data
from sybil_engine.utils.utils import ConfigurationException


networks = {
    'ZKSYNC': 'ZKSYNCERA',
    'BASE': 'BASE',
    'ARBITRUM': 'ARBITRUM',
    'OPTIMISM': 'OPTIMISM',
}


def get_sub_accounts(apiKey, secretKey):
    client = Spot(api_key=apiKey, api_secret=secretKey)

    response = client.sign_request(
        'GET',
        '/sapi/v1/sub-account/list',
        None
    )

    return [sub_account['email'] for sub_account in response['subAccounts']]


def transfer_sub_accounts(apiKey, secretKey, sub_account, assets):
    client = Spot(api_key=apiKey, api_secret=secretKey)

    for asset in assets:
        client.sub_account_universal_transfer('SPOT', 'SPOT', asset['asset'], asset['free'], fromEmail=sub_account)


def get_sub_account_balance(apiKey, secretKey, sub_account):
    client = Spot(api_key=apiKey, api_secret=secretKey)

    balances = client.sub_account_assets(sub_account)['balances']

    assets = []

    for balance in balances:
        if balance['free'] > 0:
            assets.append(
                {'asset': balance['asset'], 'free': balance['free']}
            )

    return assets


def binance_transfer_from_sub_acc(password, binance_secret):
    apiKey, secretKey = decrypt_cex_data(binance_secret, password)

    for sub_account in get_sub_accounts(apiKey, secretKey):
        assets = get_sub_account_balance(apiKey, secretKey, sub_account)
        transfer_sub_accounts(apiKey, secretKey, sub_account, assets)


def binance_withdrawal(binance_secret, password, token, amount, address, chain):
    apiKey, secretKey = decrypt_cex_data(binance_secret, password)

    client = Spot(api_key=apiKey, api_secret=secretKey)
    try:
        client.withdraw(token, amount, address, network=networks[chain])
    except ClientError as e:
        raise ConfigurationException(e.error_message)


def get_binance_deposit_addresses(password, cex_data):
    apiKey, secretKey = decrypt_cex_data(cex_data, password)

    client = Spot(api_key=apiKey, api_secret=secretKey)

    emails = get_sub_accounts(apiKey, secretKey)

    deposit_addresses = []

    for email in emails:
        deposit_addresses = deposit_addresses + client.sub_account_deposit_address(email, 'ETH')

    return deposit_addresses
