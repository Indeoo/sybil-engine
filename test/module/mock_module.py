from loguru import logger
from sybil_engine.module.module import Module


class MockModule(Module):

    def execute(self, account):
        logger.info("SuccessModule")

    def log(self):
        return "TEST FAIL MODULE"
