import random
from itertools import zip_longest

from eth_account import Account
from loguru import logger
from web3 import Web3

from sybil_engine.utils.csv_reader import read_csv_rows
from sybil_engine.utils.decryptor import decrypt_private_key
from sybil_engine.utils.file_loader import load_file_rows
from sybil_engine.utils.utils import ConfigurationException
from sybil_engine.utils.wallet_loader import load_addresses


def create_app_account(args, encryption, proxy_mode, account_creation_mode):
    if account_creation_mode == 'TXT' or account_creation_mode is None:
        return create_app_accounts_from_txt(
            args.private_keys,
            (proxy_mode, args.proxy_file),
            args.cex_addresses,
            args.starknet_addresses,
            args.password.encode('utf-8'),
            encryption
        )
    elif account_creation_mode == 'CSV':
        return create_app_accounts_from_csv(args.account_csv, args.password.encode('utf-8'), encryption)
    else:
        raise ConfigurationException("account_creation_mode should be CSV or TXT")


def create_app_accounts_from_txt(private_keys, proxy_config, cex_addresses, starknet_addresses, password, encryption):
    proxy_mode, proxy_file = proxy_config

    return create_app_account_with_proxies(
        load_addresses(cex_addresses),
        encryption,
        password,
        load_addresses(private_keys),
        load_file_rows(proxy_file),
        proxy_mode,
        load_addresses(starknet_addresses)
    )


def create_app_accounts_from_csv(account_csv, password, encryption):
    rows = read_csv_rows(account_csv)
    app_accounts = []

    starknet = False
    cex = False

    for row in rows:
        if row['ENABLE'] == 'FALSE':
            continue

        if row['CEX_ADDRESS'] != '':
            starknet = True
        if row['STARKNET_ADDRESS'] != '':
            cex = True

        if starknet and row['CEX_ADDRESS'] == '':
            raise ConfigurationException("Starknet addresses not should be less than accounts")

        if cex and row['STARKNET_ADDRESS'] == '':
            raise ConfigurationException("Cex addresses not should be less than accounts")

        if encryption:
            private_key = decrypt_private_key(row['PRIVATE_KEY'], password)
        else:
            private_key = row['PRIVATE_KEY']

        if private_key == '' or private_key is None:
            raise ConfigurationException("All private keys should exist")

        account = Web3().eth.account.from_key(private_key)

        if row['PROXY'] == '':
            proxy = None
        else:
            proxy = row['PROXY']

        app_accounts.append(
            AppAccount(
                row['ADS_ID'],
                row['CEX_ADDRESS'],
                account,
                proxy,
                row['STARKNET_ADDRESS']
            )
        )

    logger.info(f"Loaded {len(app_accounts)} accounts")
    random.shuffle(app_accounts)

    return app_accounts


def create_app_account_with_proxies(cex_addresses, encryption, password, private_keys, proxies, proxy_mode,
                                    starknet_addresses):
    if len(cex_addresses) > 0:
        if len(cex_addresses) != len(private_keys):
            raise Exception("Cex addresses should not be less than accounts")
    if len(starknet_addresses) > 0:
        if len(starknet_addresses) != len(private_keys):
            raise Exception("Starknet addresses not should be less than accounts")

    if len(private_keys) < len(proxies):
        raise ConfigurationException('There should be less or equals amount of proxies to private keys')

    accs_tulpe = list(zip_longest(private_keys, cex_addresses, proxies, starknet_addresses))
    app_accounts = []
    seen_private_keys = set()

    for index, (private_key, cex_address, proxy, starknet_address) in enumerate(accs_tulpe, start=1):
        if private_key.startswith(('#',)):
            continue
        else:
            if private_key.__contains__(":"):
                rage_acc_id, private_key = private_key.split(' : ')
                if private_key in seen_private_keys:
                    continue
                seen_private_keys.add(private_key)

            if encryption:
                private_key = decrypt_private_key(private_key, password)

            account = Web3().eth.account.from_key(private_key)

        if len(proxies) > 0:
            if proxy_mode == 'RANDOM':
                for i in range(len(app_accounts)):
                    proxy = random.choice(proxies)

            elif proxy_mode == 'STRICT':
                proxy = proxy
        else:
            for i in range(len(app_accounts)):
                proxy = None

        app_accounts = app_accounts + [AppAccount(index, proxy, account, cex_address, starknet_address)]

    logger.info(f"Loaded {len(app_accounts)} accounts")
    random.shuffle(app_accounts)

    return app_accounts


class AppAccount(Account):
    def __init__(self, app_id, proxy, account, cex_address, starknet_address):
        self.app_id = app_id
        self.proxy = proxy
        self.address = account.address
        self.key = account.key
        self.cex_address = cex_address
        self.starknet_address = starknet_address

    def __repr__(self):
        return f"[{repr(self.app_id)}] {self.address}"
