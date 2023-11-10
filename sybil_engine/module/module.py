from functools import wraps

from loguru import logger

from sybil_engine.domain.balance.balance import NotEnoughNativeBalance
from sybil_engine.utils.utils import ConfigurationException, ModuleException
from enum import Enum


class Order(Enum):
    STRICT = 1
    RANDOM = 2


class Module:
    module_name = 'None'
    allowed_chains = 'None'
    random_order = Order.STRICT
    repeat_conf = 'repeats'

    def __init__(self, min_native_balance, storage, auto_withdrawal=False):
        self.min_native_balance = min_native_balance
        self.storage = storage
        self.auto_withdrawal = auto_withdrawal

    def execute(self, *args):
        pass

    def log(self):
        pass

    def handle(self, e):
        raise e

    def parse_params(self, module_params):
        return []

    def sleep_after(self):
        return True

    def validate_supported_chain(self, chain):
        if chain not in self.allowed_chains:
            raise ConfigurationException(f"{self.module_name} does not support {chain}, skip")

    def order(self):
        return self.random_order


class RepeatableModule(Module):

    def __init__(self, min_native_balance, storage, auto_withdrawal, repeats):
        super().__init__(min_native_balance, storage, auto_withdrawal)
        self.repeats = repeats

    @staticmethod
    def repeatable_log(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            module_name = self.module_name
            self.storage.setdefault(module_name, 1)

            logger.info(f"({self.storage.get(module_name)}/{self.repeats}) {module_name} {args[-1].address}")

            if self.storage.get(module_name) == self.repeats:
                self.storage.put(module_name, 1)
            else:
                self.storage.put(module_name, self.storage.get(module_name) + 1)

            return func(self, *args, **kwargs)

        return wrapper

    def handle(self, e):
        if isinstance(e, NotEnoughNativeBalance):
            raise e

        raise ModuleException("Fail to complete step of the repeatable module") from e
