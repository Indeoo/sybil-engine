from sybil_engine.module.modules import GenericModules
from test.module.mock_fail_module import MockFailModule
from test.module.mock_module import MockModule
from test.module.repeatable_mock_module import RepeatableMockModule

module_map = {
    1000: (MockModule, 'mock_config'),
    1001: (MockFailModule, 'mock_fail_config'),
    1002: (RepeatableMockModule, 'repeatable_mock_config')
}


class TestModules(GenericModules):
    def get_module_map(self):
        return module_map

    def get_swap_apps(self):
        return ['RepeatableMockModule', 'MockModule', 'MockFailModule']
