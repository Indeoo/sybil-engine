from loguru import logger
from sybil_engine.module.module import Module


class MockModule(Module):
    module_name = 'MockModule'

    def __init__(self, min_native_balance, storage, auto_withdrawal):
        super().__init__(min_native_balance, storage, auto_withdrawal)

    def execute(self, account):
        logger.info("SuccessModule")

    def log(self):
        return "TEST FAIL MODULE"
