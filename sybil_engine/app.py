from loguru import logger
from sybil_engine.config.app_config import set_network, set_gas_prices, set_dex_retry_interval, set_module_data, \
    set_okx_config
from sybil_engine.module.execution_planner import create_execution_plans
from sybil_engine.module.module_executor import ModuleExecutor
from sybil_engine.utils.accumulator import print_accumulated
from sybil_engine.utils.app_account_utils import create_app_accounts
from sybil_engine.utils.arguments_parser import parse_arguments
from sybil_engine.utils.configuration_loader import load_config_maps, load_module_vars
from sybil_engine.utils.fee_storage import print_fee
from sybil_engine.utils.logs import load_logger
from sybil_engine.utils.telegram import set_telegram_api_chat_id, set_telegram_api_key, send_to_bot
from sybil_engine.utils.utils import ConfigurationException
from sybil_engine.utils.wallet_loader import load_addresses


def prepare_launch_without_data(modules_data_file):
    config_map, module_map = load_config_maps()
    modules_data = load_module_vars(modules_data_file)['modules_data']

    load_logger(send_to_bot, config_map['telegram_enabled'], config_map['telegram_log_level'])

    args = parse_arguments(config_map['password'], module_map['module'])

    set_telegram_api_chat_id(config_map['telegram_api_chat_id'])
    set_telegram_api_key(config_map['telegram_api_key'])

    module_config = module_map['scenario_config'] if args.module == 'SCENARIO' else {
        'scenario_name': args.module,
        'scenario': [
            {'module': args.module, 'params': modules_data.get_module_config_by_name(args.module, module_map)}]
    }

    config = (
        modules_data,
        config_map['encryption'],
        module_map['min_native_interval'],
        config_map['proxy_mode'],
        (
            config_map['cex_data'],
            config_map.get('auto_withdrawal', False),
            config_map.get('min_auto_withdraw_interval', {'from': 0.1, 'to': 0.2}),
            config_map['withdraw_interval']
        ),
        module_map['sleep_interval'],
        module_map['swap_retry_sleep_interval'],
        config_map['gas_prices']
    )

    launch_app(args, module_config, config)


def launch_app(args, module_config, config):
    (modules_data, encryption, min_native_interval, proxy_mode, okx, sleep_interval, swap_retry_sleep_interval,
     gas_price) = config

    set_network(args.network)
    set_dex_retry_interval(swap_retry_sleep_interval)
    set_gas_prices(gas_price)
    set_module_data(modules_data)
    set_okx_config((args.password.encode('utf-8'), okx))

    logger.info(f"START {module_config['scenario_name']} application in {args.network}")

    if not all(modules_data.get_module_class_by_name(module['module']) for module in module_config['scenario']):
        raise ConfigurationException("Non-existing module is used")

    accounts = create_app_accounts(
        load_addresses(args.private_keys),
        (proxy_mode, args.proxy_file),
        load_addresses(args.cex_addresses),
        load_addresses(args.starknet_addresses),
        args.password.encode('utf-8'),
        encryption
    )

    execution_plans = create_execution_plans(accounts, min_native_interval, module_config, modules_data)

    for index, (account, min_native_balance, modules) in execution_plans:
        logger.info(f"[{index}/{len(accounts)}][{account.app_id}] {account.address}")
        ModuleExecutor(sleep_interval).execute_modules(modules, account)

    print_fee()
    print_accumulated()
