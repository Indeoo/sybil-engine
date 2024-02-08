from loguru import logger

from sybil_engine.config.app_config import set_network, set_gas_prices, set_dex_retry_interval, set_module_data, \
    set_cex_data
from sybil_engine.module.execution_planner import create_execution_plans
from sybil_engine.module.module_executor import ModuleExecutor
from sybil_engine.utils.accumulator import print_accumulated, add_accumulator_str
from sybil_engine.utils.app_account_utils import create_app_account
from sybil_engine.utils.arguments_parser import parse_arguments, parse_profile
from sybil_engine.utils.configuration_loader import load_config_maps, load_module_vars
from sybil_engine.utils.fee_storage import print_fee
from sybil_engine.utils.logs import load_logger
from sybil_engine.utils.telegram import set_telegram_api_chat_id, set_telegram_api_key, send_to_bot
from sybil_engine.utils.utils import ConfigurationException


def prepare_launch_without_data(modules_data_file):
    config_map, module_map = load_config_maps()
    modules_data = load_module_vars(modules_data_file)['modules_data']

    load_logger(send_to_bot, config_map['telegram_enabled'], config_map['telegram_log_level'])

    set_telegram_api_chat_id(config_map['telegram_api_chat_id'])
    set_telegram_api_key(config_map['telegram_api_key'])

    args = parse_arguments(config_map['password'], module_map['module'])

    if 'shell_mode' not in config_map:
        config_map['shell_mode'] = 'classic'

    if 'account_creation_mode' not in config_map:
        config_map['account_creation_mode'] = 'TXT'

    if 'cex_address_validation' not in config_map:
        config_map['cex_address_validation'] = True

    if 'interactive_confirmation' not in config_map:
        config_map['interactive_confirmation'] = True

    if config_map['shell_mode'] == 'interactive':
        logger.info("Choose module (by id):")

        for module_id, module in modules_data.get_module_map().items():
            module_name = get_module_name(module)
            logger.info(f"  {module_id} {module_name}")

        choice = input()
        selected_module = modules_data.get_module_map()[int(choice)]
        module_name = get_module_name(selected_module)
    else:
        module_name = args.module

    module_config = module_map['scenario_config'] if module_name == 'SCENARIO' else {
        'scenario_name': module_name,
        'scenario': [
            {'module': module_name, 'params': modules_data.get_module_config_by_name(module_name, module_map)}]
    }

    config = (
        modules_data,
        config_map['encryption'],
        module_map['min_native_interval'],
        config_map['proxy_mode'],
        config_map['cex_data'],
        module_map['sleep_interval'],
        module_map['swap_retry_sleep_interval'],
        config_map['gas_prices'],
        config_map['account_creation_mode'],
        config_map['cex_address_validation'],
        config_map['interactive_confirmation']
    )

    launch_app(args, module_config, config)


def get_module_name(module):
    if module[0] is not None:
        return module[0].module_name
    else:
        return 'SCENARIO'


def launch_app(args, module_config, config):
    (modules_data, encryption, min_native_interval, proxy_mode, cex_data, sleep_interval, swap_retry_sleep_interval,
     gas_price, account_creation_mode, cex_address_validation, interactive_confirmation) = config

    set_network(args.network)
    set_dex_retry_interval(swap_retry_sleep_interval)
    set_gas_prices(gas_price)
    set_module_data(modules_data)
    set_cex_data((args.password.encode('utf-8'), cex_data))

    logger.info(f"START {module_config['scenario_name']} module in {args.network}")

    profile = parse_profile().profile
    logger.info(f"Profile {profile} activated")

    if not all(modules_data.get_module_class_by_name(module['module']) for module in module_config['scenario']):
        raise ConfigurationException("Non-existing module is used")

    accounts = create_app_account(args, encryption, proxy_mode, account_creation_mode, cex_address_validation)

    execution_plans = create_execution_plans(accounts, min_native_interval, module_config, modules_data)

    if interactive_confirmation:
        logger.info("Are you sure you want to start with this configuration? Y/n")
        choice = input()
        if choice != "Y":
            logger.info("Exiting")
            return

    try:
        proceed_accounts(accounts, execution_plans, sleep_interval)
    finally:
        print_fee()
        print_accumulated()


def proceed_accounts(accounts, execution_plans, sleep_interval):
    for account in accounts:
        add_accumulator_str("Pending accounts: ", account)

    for index, (account, modules) in execution_plans:
        logger.info(f"[{index}/{len(accounts)}][{account.app_id}] {account.address}")
        ModuleExecutor().execute_modules(modules, account, sleep_interval)
