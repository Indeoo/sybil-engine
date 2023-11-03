from loguru import logger
from collections import defaultdict

from sybil_engine.config.app_config import get_okx
from sybil_engine.domain.balance.balance import NotEnoughNativeBalance
from sybil_engine.module.module import RepeatableModule
from sybil_engine.utils.accumulator import add_accumulator_str
from sybil_engine.utils.okx import withdrawal
from sybil_engine.utils.utils import randomized_sleeping, ModuleException, AccountException


class AccountAccumulator:

    def __init__(self):
        self.accumulator = {}

    def put(self, key, value):
        self.accumulator[key] = value

    def get(self, key):
        return self.accumulator.get(key)


class ModuleExecutor:

    def __init__(self, sleep_interval):
        self.sleep_interval = sleep_interval

    def execute_modules(self, modules, account):
        executed_counter = defaultdict(int)

        try:
            for module, module_args in modules:
                executed_counter[type(module)] += 1
                self.execute_module(module_args, account, module, executed_counter[type(module)])
        except AccountException as e:
            logger.error(f'Error, skip account {account}: {e}')
            add_accumulator_str("Failed accounts: ", account)
        except Exception as e:
            logger.error(f'Error, skip account {account}: {e}')
            add_accumulator_str("Failed accounts: ", account)

    def execute_module(self, module_args, account, module, counter):
        try:
            if issubclass(type(module), RepeatableModule):
                logger.info(f"({counter}/{module.repeats}) {module.module_name} {account.address}")
            parsed_module_args = module.parse_params(module_args)
            module.execute(*parsed_module_args, account)
            if module.sleep_after():
                randomized_sleeping(self.sleep_interval)
        except ModuleException as e:
            logger.info(e.message)
        except NotEnoughNativeBalance as e:
            okx_secret, (cex_data, auto_withdrawal, withdraw_interval) = get_okx()

            if auto_withdrawal and e.chain in ['ZKSYNC', 'LINEA'] and module.auto_withdrawal:
                withdrawal(account.address, okx_secret, e.chain, cex_data, withdraw_interval)
                randomized_sleeping({'from': 60 * 5, 'to': 60 * 10})
                self.execute_module(module_args, account, module, counter)
            else:
                raise AccountException(e)
