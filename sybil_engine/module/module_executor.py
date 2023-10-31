import itertools
import random

from loguru import logger

from sybil_engine.config.app_config import get_okx
from sybil_engine.domain.balance.balance import NotEnoughNativeBalance
from sybil_engine.module.module import Order
from sybil_engine.utils.okx import withdrawal
from sybil_engine.utils.utils import randomized_sleeping, ModuleException, AccountException


def split_list(items):
    result = []
    sublist = []
    for module, config in items:
        item_tuple = (module, config)
        if 'order' in config:
            order = Order.__members__[config['order']]
        else:
            order = module.order()

        if order == Order.STRICT:
            if sublist:
                result.append(sublist)
                sublist = []
            result.append([item_tuple])
        else:
            sublist.append(item_tuple)
    if sublist:
        result.append(sublist)
    return result


def randomize_modules(modules):
    arrays = split_list(modules)
    [random.shuffle(array) for array in arrays]
    return list(itertools.chain(*arrays))


def execute_modules(sleep_interval, module_classes, account, min_native_balance):
    modules = [(module_class(min_native_balance, account), module_args) for module_class, module_args in module_classes]
    randomized_modules = randomize_modules(modules)

    for module, module_args in randomized_modules:
        execute_module(sleep_interval, module_args, account, module)


def execute_module(sleep_interval, module_args, account, module):
    try:
        logger.info(f"Start {module.log()} Module {account.address}")
        module.set_auto_withdrawal(module_args)
        parsed_module_args = module.parse_params(module_args)
        module.execute(*parsed_module_args, account)
        if module.sleep_after():
            randomized_sleeping(sleep_interval)
    except ModuleException as e:
        logger.info(e.message)
    except NotEnoughNativeBalance as e:
        okx_secret, (cex_data, auto_withdrawal, withdraw_interval) = get_okx()

        if auto_withdrawal and e.chain in ['ZKSYNC', 'LINEA'] and module.auto_withdrawal:
            withdrawal(account.address, okx_secret, e.chain, cex_data, withdraw_interval)
            randomized_sleeping({'from': 60 * 5, 'to': 60 * 10})
            execute_module(sleep_interval, module_args, account, module)
        else:
            raise AccountException(e)
