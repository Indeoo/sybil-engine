class Module:
    module_name = 'None'

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

    def set_auto_withdrawal(self, module_params):
        if module_params.get('auto_withdrawal', False):
            self.auto_withdrawal = True
