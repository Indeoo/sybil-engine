from sybil_engine.utils.utils import ConfigurationException


class GenericSwapFacade:
    def __init__(self, dex_classes, swap_apps):
        self.dex_classes = dex_classes
        self.swap_apps = swap_apps

    def swap(self, account, amount_to_swap, chain_instance, pair, swap_app, from_token, to_token, web3):
        slippage_coef = 1 - pair['slippage'] * 0.01

        dex = self.get_dex(pair, swap_app, chain_instance, web3)
        dex.swap(amount_to_swap, from_token, to_token, slippage_coef, account)

    def get_dex(self, pair, swap_app, chain_instance, web3):
        dex_class, additional_args = self.get_dex_classes(pair).get(swap_app, (None, None))
        if dex_class is None:
            raise ConfigurationException(f"Wrong pair.py configuration for {swap_app}")

        return dex_class(chain_instance, web3, **additional_args)

    def get_swap_apps(self):
        return [swap_app_name.dex_name for swap_app_name in self.get_all_swap_apps().keys()]

    def get_swap_apps_by_chain(self, chain_name):
        filtered_apps = {app: chains for app, chains in self.get_all_swap_apps().items() if chain_name in chains}

        return [swap_app_name.dex_name for swap_app_name in filtered_apps.keys()]

    def get_all_swap_apps(self):
        return self.swap_apps

    def get_dex_classes(self, pair):
        return self.dex_classes
