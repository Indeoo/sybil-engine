from loguru import logger

from sybil_engine.utils.accumulator import add_accumulator_str, remove_accumulator_str
from sybil_engine.utils.utils import randomized_sleeping, ModuleException, print_exception_chain, ConfigurationException


class ModuleExecutor:
    def execute_modules(self, modules, account, sleep_interval):
        try:
            for module, module_args in modules:
                self.execute_module(module_args, account, module, sleep_interval)
            add_accumulator_str("Finished accounts: ", account)
            remove_accumulator_str("Pending accounts: ", account)
        except ConfigurationException as e:
            raise Exception(f"Configuration error in {module.module_name}: {e}")
        except Exception as e:
            logger.error(f'Error, skip {account}:')
            print_exception_chain(e)
            add_accumulator_str("Failed accounts: ", account)

    def execute_module(self, module_args, account, module, sleep_interval):
        try:
            parsed_module_args = module.parse_params(module_args)
            try:
                module.execute(*parsed_module_args, account)
                if module.sleep_after():
                    randomized_sleeping(sleep_interval)
            except Exception as e:
                module.handle(e)
        except ModuleException as e:
            print_exception_chain(e)
