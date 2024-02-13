from sybil_engine.config.app_config import get_cex_data
from sybil_engine.utils.binance_utils import get_binance_deposit_addresses
from sybil_engine.utils.okx_utils import get_okx_deposit_addresses


def get_cex_addresses():
    password, cex_data = get_cex_data()

    return get_okx_deposit_addresses(password, cex_data['okx']) #+ get_binance_deposit_addresses(password, cex_data['binance'])
