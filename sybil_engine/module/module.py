from sybil_engine.utils.utils import ConfigurationException


class Module:
    module_name = 'None'
    allowed_chains = 'None'

    def __init__(self, min_native_balance, account):
        self.min_native_balance = min_native_balance
        self.account = account
        self.auto_withdrawal = False

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

    def set_auto_withdrawal(self, module_params):
        if module_params.get('auto_withdrawal', False):
            self.auto_withdrawal = True
