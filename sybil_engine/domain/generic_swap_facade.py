from loguru import logger

from sybil_engine.data.contracts import get_contracts_for_chain
from sybil_engine.data.tokens import get_tokens_for_chain
from sybil_engine.domain.balance.balance import NotEnoughERC20Balance
from sybil_engine.utils.utils import ConfigurationException


class GenericSwapFacade:
    def swap(self, account, amount_to_swap, chain_instance, pair, swap_app, from_token, to_token, web3):
        if amount_to_swap.wei == 0 and amount_to_swap.token != chain_instance['gas_token']:
            raise NotEnoughERC20Balance(f"Can't swap {amount_to_swap.log_line()}")

        logger.info(f"Swap {amount_to_swap.log_line()} -> {to_token} in {swap_app} ({chain_instance['chain']})")

        chain_contracts = get_contracts_for_chain(chain_instance['chain'])
        tokens = get_tokens_for_chain(chain_instance['chain'])

        slippage_coef = 1 - pair['slippage'] * 0.01

        dex = self.get_dex(chain_contracts, pair, swap_app, tokens, chain_instance, web3)

        dex.swap_with_retry(amount_to_swap, from_token, to_token, slippage_coef, account)

    def get_dex(self, chain_contracts, pair, swap_app, tokens, chain_instance, web3):
        dex_class, additional_args = self.get_dex_classes(pair).get(swap_app, (None, None))
        if dex_class is None:
            raise ConfigurationException(f"Wrong pair.py configuration for {swap_app}")

        return dex_class(chain_contracts, tokens, chain_instance, web3, **additional_args)

    def get_swap_apps(self):
        return [swap_app_name.dex_name for swap_app_name in self.get_all_swap_apps().keys()]

    def get_swap_apps_by_chain(self, chain_name):
        filtered_apps = {app: chains for app, chains in self.get_all_swap_apps().items() if chain_name in chains}

        return [swap_app_name.dex_name for swap_app_name in filtered_apps.keys()]

    def get_all_swap_apps(self):
        pass

    def get_dex_classes(self, pair):
        pass
