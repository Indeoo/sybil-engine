import itertools
import random

from loguru import logger

from sybil_engine.config.app_config import get_okx_config
from sybil_engine.domain.balance.balance import NotEnoughNativeBalance
from sybil_engine.module.module import Order
from sybil_engine.utils.okx import withdrawal
from sybil_engine.utils.utils import randomized_sleeping, ModuleException, AccountException


def split_list(items):
    result = []
    sublist = []
    for module, config in items:
        if module.order() == Order.STRICT:
            if sublist:  # if there are already items in sublist, append it to result and start a new sublist
                result.append(sublist)
                sublist = []
            result.append([(module, config)])  # append strict module as a single-element sublist
        else:  # module.value_type == 'RANDOM'
            sublist.append((module, config))  # append random module to current sublist
    if sublist:  # append any remaining items
        result.append(sublist)
    return result


def randomize_modules(modules):
    arrays = split_list(modules)
    [random.shuffle(array) for array in arrays]
    return list(itertools.chain(*arrays))


def execute_modules(okx_secret, sleep_interval, module_classes, account, min_native_balance):
    modules = []

    for module_class, module_args in module_classes:
        module = module_class(min_native_balance, account)
        modules.append((module, module_args))

    for module, module_args in randomize_modules(modules):
        logger.info(f"Start {module.log()} Module {account.address}")
        execute_module(okx_secret, sleep_interval, module_args, account, module)


def execute_module(okx_secret, sleep_interval, module_args, account, app_module):
    try:
        app_module.set_auto_withdrawal(module_args)
        parsed_module_args = app_module.parse_params(module_args)
        app_module.execute(*parsed_module_args, account)
        if app_module.sleep_after():
            randomized_sleeping(sleep_interval)
    except ModuleException as e:
        logger.info(e.message)
    except NotEnoughNativeBalance as e:
        cex_data, auto_withdrawal, withdraw_interval = get_okx_config()

        if auto_withdrawal and e.chain in ['ZKSYNC', 'LINEA'] and app_module.auto_withdrawal:
            withdrawal(account.address, okx_secret, e.chain, cex_data, withdraw_interval)
            randomized_sleeping({'from': 60 * 5, 'to': 60 * 10})
            execute_module(okx_secret, sleep_interval, module_args, account, app_module)
        else:
            raise AccountException(e)
