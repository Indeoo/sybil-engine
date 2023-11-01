import itertools
import random

from loguru import logger
from collections import defaultdict

from sybil_engine.config.app_config import get_okx
from sybil_engine.domain.balance.balance import NotEnoughNativeBalance
from sybil_engine.module.module import Order, RepeatableModule
from sybil_engine.utils.okx import withdrawal
from sybil_engine.utils.utils import randomized_sleeping, ModuleException, AccountException, interval_to_int


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


def repeats(module_params, repeat_conf):
    if repeat_conf not in module_params:
        return range(1)
    else:
        return range(interval_to_int(module_params[repeat_conf]))


def execute_modules(sleep_interval, module_classes, account, min_native_balance):
    modules = []

    for module_class, module_args in module_classes:
        if issubclass(module_class, RepeatableModule):
            counted_repeats = repeats(module_args, module_class.repeat_conf)
            for i in counted_repeats:
                tulpe = (module_class(min_native_balance, account, len(counted_repeats)), module_args)
                modules.append(tulpe)
        else:
            tulpe = (module_class(min_native_balance, account), module_args)
            modules.append(tulpe)

    executed_counter = defaultdict(int)

    for module, module_args in randomize_modules(modules):
        executed_counter[type(module)] += 1
        execute_module(sleep_interval, module_args, account, module, executed_counter[type(module)])


def execute_module(sleep_interval, module_args, account, module, counter):
    try:
        if issubclass(type(module), RepeatableModule):
            logger.info(f"({counter}/{module.repeats}) {module.module_name} {account.address}")
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
            execute_module(sleep_interval, module_args, account, module, counter)
        else:
            raise AccountException(e)
