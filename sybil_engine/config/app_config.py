network = None
dex_retry_interval = None
gas_prices_gwei = None
module_data = None
okx = None, (None, None, None, None)


def set_network(value):
    global network
    network = value


def get_network():
    return network


def set_dex_retry_interval(value):
    global dex_retry_interval
    dex_retry_interval = value


def get_dex_retry_interval():
    return dex_retry_interval


def set_gas_prices(value):
    global gas_prices_gwei
    gas_prices_gwei = value


def get_gas_prices():
    return gas_prices_gwei


def set_module_data(value):
    global module_data
    module_data = value


def get_module_data():
    return module_data


def set_okx_config(value):
    global okx
    okx = value


def get_okx():
    return okx
