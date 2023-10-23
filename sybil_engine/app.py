import random

from loguru import logger
from sybil_engine.config.app_config import set_network, set_gas_prices, set_dex_retry_interval, set_module_data
from sybil_engine.domain.balance.balance_utils import interval_to_eth_balance
from sybil_engine.module.module_executor import execute_modules
from sybil_engine.utils.accumulator import print_accumulated, add_accumulator_str
from sybil_engine.utils.app_account_utils import create_app_accounts
from sybil_engine.utils.arguments_parser import parse_arguments
from sybil_engine.utils.fee_storage import print_fee
from sybil_engine.utils.logs import load_logger
from sybil_engine.utils.telegram import set_telegram_api_chat_id, set_telegram_api_key, send_to_bot
from sybil_engine.utils.utils import ConfigurationException, AccountException
from sybil_engine.utils.wallet_loader import load_addresses


def prepare_launch(config_map, module_map, modules_data):
    set_telegram_api_chat_id(config_map['telegram_api_chat_id'])
    set_telegram_api_key(config_map['telegram_api_key'])

    load_logger(send_to_bot, config_map['telegram_enabled'], config_map['telegram_log_level'])
    args = parse_arguments(config_map['password'], module_map['module'])
    module_config = module_map['scenario_config'] if args.module == 'SCENARIO' else {
        'scenario_name': args.module,
        'scenario': [
            {'module': args.module, 'params': modules_data.get_module_config_by_name(args.module)}]
    }
    okx = (config_map['cex_data'], config_map['auto_withdrawal'], config_map['withdraw_interval'])

    config = (
        modules_data,
        config_map['encryption'],
        module_map['min_native_interval'],
        config_map['proxy_mode'],
        okx,
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

    okx_secret = args.password.encode('utf-8')

    accounts = create_app_accounts(
        load_addresses(args.private_keys),
        (proxy_mode, args.proxy_file),
        load_addresses(args.cex_addresses),
        load_addresses(args.starknet_addresses),
        args.password.encode('utf-8'),
        encryption
    )
    random.shuffle(accounts)

    modules = [
        (modules_data.get_module_class_by_name(module['module']), module['params']) for module in
        module_config['scenario']
    ]

    logger.info(f"START {module_config['scenario_name']} application in {args.network}")

    if not all(modules_data.get_module_class_by_name(module['module']) for module in module_config['scenario']):
        raise ConfigurationException("Non-existing module is used")

    process_accounts(accounts, okx_secret, min_native_interval, modules, okx, sleep_interval)

    print_fee()
    print_accumulated()


def process_accounts(app_accounts, okx_secret, min_native_interval, modules, okx_config, sleep_interval):
    logger.info(f"Loaded {len(app_accounts)} accounts")

    for index, account in enumerate(app_accounts, 1):
        logger.info(f"[{index}/{len(app_accounts)}][{account.app_id}] {account.address}")

        min_native_balance = interval_to_eth_balance(min_native_interval, account, None, None)

        try:
            execute_modules(okx_secret, sleep_interval, modules, account, okx_config, min_native_balance)
        except AccountException as e:
            logger.error(f'Error, skip account {account}: {e}')
            add_accumulator_str("Failed accounts: ", account)
        except Exception as e:
            logger.error(f'Error, skip account {account}: {e}')
            add_accumulator_str("Failed accounts: ", account)
