from sybil_engine.config.app_config import get_network, get_gas_prices
from sybil_engine.data.exception import NetworkNotFoundException
from sybil_engine.utils.file_loader import load_json_resource

ids_chain = {
    324: 'ZKSYNC',  # MAIN
    260: 'ZKSYNC',  # LOCAL
    42161: 'ARBITRUM',
    442161: 'ARBITRUM',  # LOCAL
    421613: 'ARBITRUM',  # LOCAL
    59144: 'LINEA',
    559144: 'LINEA',  # LOCAL
    534352: 'SCROLL',
    5534352: 'SCROLL',  # LOCAL
    8453: 'BASE',
    18453: 'BASE',
    56: 'BSC',
    250: 'FANTOM',
    10: 'OPTIMISM',
    137: 'POLYGON',
    43114: 'AVALANCHE'
}


def get_chain_instance(chain: str):
    return get_chain_instance_for_network(chain, get_network())


def get_chain_instance_for_network(chain: str, network: str):
    rpcs = get_rpcs(network).copy()

    if chain not in rpcs:
        raise NetworkNotFoundException(f"{chain} not found")

    rpc = rpcs[chain]

    gas_prices_gwei = get_gas_prices()
    rpc['l1_gas_price_gwei'] = gas_prices_gwei['ETH_MAINNET']
    if 'gas_price_gwei' not in rpc:
        rpc['gas_price_gwei'] = gas_prices_gwei[chain]

    rpc['chain'] = chain

    return rpc


def get_rpcs(network):
    if network == 'MAIN':
        return load_json_resource("main/networks.json")
    elif network == 'LOCAL':
        return load_json_resource("local/networks.json")
    elif network == 'GOERLI':
        return load_json_resource("goerli/networks.json")
    else:
        raise NetworkNotFoundException(f"Network {network} not found")
