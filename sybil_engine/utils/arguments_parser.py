import argparse
import os


def parse_arguments(default_password, default_module):
    parser = argparse.ArgumentParser(description='Process arguments.')

    parser.add_argument('--private_keys', type=str, required=False,
                        default=os.environ.get('PRIVATE_KEYS', 'wallets/private_keys.txt'),
                        help='a string to be processed')
    parser.add_argument('--cex_addresses', type=str, required=False,
                        default=os.environ.get('CEX_ADDRESSES', 'wallets/cex_addresses.txt'),
                        help='a string to be processed')
    parser.add_argument('--starknet_addresses', type=str, required=False,
                        default=os.environ.get('STARKNET_ADDRESSES', 'wallets/starknet_addresses.txt'),
                        help='a string to be processed')
    parser.add_argument('--proxy_file', type=str, required=False,
                        default=os.environ.get('PROXY_FILE', 'wallets/proxy.txt'),
                        help='a string to be processed')
    parser.add_argument('--password', type=str, required=False, default=os.environ.get('PASSWORD', default_password),
                        help='a string to be processed')
    parser.add_argument('--network', type=str, required=False, default=os.environ.get('NETWORK', 'MAIN'),
                        help='a string to be processed')
    parser.add_argument('--module', type=str, required=False, default=os.environ.get('MODULE', default_module),
                        help='a string to be processed')

    return parser.parse_args()
