from loguru import logger

from sybil_engine.domain.balance.balance import NotEnoughNativeBalance
from sybil_engine.utils.accumulator import add_accumulator_str
from sybil_engine.utils.utils import randomized_sleeping, ModuleException, AccountException, print_exception_chain


class ModuleExecutor:

    def __init__(self, sleep_interval):
        self.sleep_interval = sleep_interval

    def execute_modules(self, modules, account):
        try:
            for module, module_args in modules:
                self.execute_module(module_args, account, module)
        except AccountException as e:
            logger.error(f'Error, skip {account}:')
            print_exception_chain(e)
            add_accumulator_str("Failed accounts: ", account)
        except Exception as e:
            logger.error(f'Error, skip {account}:')
            print_exception_chain(e)
            add_accumulator_str("Failed accounts: ", account)

    def execute_module(self, module_args, account, module):
        try:
            parsed_module_args = module.parse_params(module_args)
            try:
                module.execute(*parsed_module_args, account)
                if module.sleep_after():
                    randomized_sleeping(self.sleep_interval)
            except Exception as e:
                module.handle(e)
        except ModuleException as e:
            print_exception_chain(e)
