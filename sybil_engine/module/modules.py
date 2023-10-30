class GenericModules:
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
        pass

    def get_swap_apps(self):
        pass

    def get_supported_chains(self):
        return ['ZKSYNC', 'ARBITRUM', 'BASE', 'BSC', 'POLYGON', 'AVALANCHE', 'OPTIMISM', 'FANTOM', 'STARKNET', 'LINEA', 'SCROLL']
