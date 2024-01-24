from sybil_engine.config.app_config import get_network, get_gas_prices
from sybil_engine.data.exception import NetworkNotFoundException
from sybil_engine.utils.file_loader import load_json_resource
from sybil_engine.utils.utils import ConfigurationException

main_ids = {
    324: 'ZKSYNC',
    42161: 'ARBITRUM',
    59144: 'LINEA',
    534352: 'SCROLL',
    8453: 'BASE',
    56: 'BSC',
    250: 'FANTOM',
    10: 'OPTIMISM',
    137: 'POLYGON',
    43114: 'AVALANCHE',
    42766: 'ZKFAIR',
    42170: 'ARBITRUM_NOVA',
    1116: 'COREDAO',
    169: 'MANTA',
    7777777: 'ZORA',
    1101: 'POLYGON_ZK'
}

local_ids = {
    260: 'ZKSYNC',
    421613: 'ARBITRUM',
    559144: 'LINEA',
    5534352: 'SCROLL',
    18453: 'BASE',
}


def get_ids_chain():
    return main_ids.copy() if get_network() == 'MAIN' else local_ids.copy()


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
        if chain not in gas_prices_gwei:
            raise ConfigurationException(f"Gas price for {chain} not found in gas_price_gwei")
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
