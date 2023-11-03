from sybil_engine.utils.utils import ConfigurationException
from enum import Enum


class Order(Enum):
    STRICT = 1
    RANDOM = 2


class Module:
    module_name = 'None'
    allowed_chains = 'None'
    random_order = Order.STRICT
    repeat_conf = 'repeats'

    def __init__(self, min_native_balance, accumulator, auto_withdrawal=False):
        self.min_native_balance = min_native_balance
        self.accumulator = accumulator
        self.auto_withdrawal = auto_withdrawal

    def execute(self, *args):
        pass

    def log(self):
        pass

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

    def __init__(self, min_native_balance, accumulator, auto_withdrawal, repeats):
        super().__init__(min_native_balance, accumulator, auto_withdrawal)
        self.repeats = repeats
