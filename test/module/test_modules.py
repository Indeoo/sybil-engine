from sybil_engine.module.modules import GenericModules
from test.module.mock_fail_module import MockFailModule
from test.module.mock_module import MockModule

module_map = {
    1000: (MockModule, 'mock_config'),
    1001: (MockFailModule, 'mock_fail_config')
}


class TestModules(GenericModules):
    def get_module_map(self):
        return module_map

    def get_swap_apps(self):
        return ['MockModule', 'MockFailModule']