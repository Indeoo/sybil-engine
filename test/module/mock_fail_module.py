from sybil_engine.module.module import Module
from sybil_engine.utils.utils import AccountException


class MockFailModule(Module):

    def execute(self, account):
        raise AccountException("test exception")

    def log(self):
        return "TEST FAIL MODULE"
