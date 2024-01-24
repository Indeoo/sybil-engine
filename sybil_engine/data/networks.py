from sybil_engine.config.app_config import get_network, get_gas_prices
from sybil_engine.data.exception import NetworkNotFoundException
from sybil_engine.utils.file_loader import load_json_resource
from sybil_engine.utils.utils import ConfigurationException


def get_ids_chain():
    return {info["chain_id"]: chain for chain, info in get_rpcs(get_network()).items()}


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
