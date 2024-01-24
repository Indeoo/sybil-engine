from sybil_engine.config.app_config import get_network
from sybil_engine.data.networks import get_rpcs


class Modules:
    def __init__(self, module_map, swap_facade):
        self.module_map = module_map
        self.swap_facade = swap_facade

    def get_module_config_by_name(self, module_name, module_map):
        for key, (module_class, config) in self.get_module_map().items():
            if module_class and (module_class.module_name == module_name):
                if config is None:
                    return {}
                elif isinstance(config, str):
                    return module_map[config]
                else:
                    return config
        return 0

    def get_module_class_by_name(self, module_name):
        for key, (module_class, config) in self.get_module_map().items():
            if module_class and (module_class.module_name == module_name):
                return module_class
        return 0

    def get_modules(self):
        return [module[0] for module in self.get_module_map().values()]

    def get_module_map(self):
        return self.module_map

    def get_swap_apps(self):
        return self.swap_facade.get_swap_apps()

    def get_supported_chains(self):
        return list(get_rpcs(get_network()).copy().keys())
