from loguru import logger

from sybil_engine.domain.balance.balance import NotEnoughNativeBalance
from sybil_engine.utils.okx import withdrawal
from sybil_engine.utils.utils import randomized_sleeping, ModuleException, AccountException


def execute_modules(okx_secret, sleep_interval, modules, account, okx_config, min_native_balance):
    for app_module_class, module_args in modules:
        app_module = app_module_class(min_native_balance, account)

        logger.info(f"Start {app_module.log()} Module {account.address}")

        execute_module(okx_secret, sleep_interval, app_module_class, module_args, okx_config, account, app_module)


def execute_module(okx_secret, sleep_interval, app_module_class, module_args, okx_config, account, app_module):
    try:
        app_module.set_auto_withdrawal(module_args)
        parsed_module_args = app_module.parse_params(module_args)
        app_module.execute(*parsed_module_args, account)
        if app_module.sleep_after():
            randomized_sleeping(sleep_interval)
    except ModuleException as e:
        logger.info(e.message)
    except NotEnoughNativeBalance as e:
        cex_data, auto_withdrawal, withdraw_interval = okx_config

        if auto_withdrawal and e.chain in ['ZKSYNC', 'LINEA'] and app_module.auto_withdrawal:
            withdrawal(account.address, okx_secret, e.chain, cex_data, withdraw_interval)
            randomized_sleeping({'from': 60 * 5, 'to': 60 * 10})
            execute_module(okx_secret, sleep_interval, app_module_class, module_args, okx_config, account, app_module)
        else:
            raise AccountException(e)
