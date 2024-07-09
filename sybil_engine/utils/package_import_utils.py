import importlib.util
import os
import sys


def import_all_variables_from_directory(directory_path):
    scenarios = []

    for filename in os.listdir(directory_path):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]
            module_path = os.path.join(directory_path, filename)

            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            for var_name in dir(module):
                if not var_name.startswith('_'):
                    scenario = getattr(module, var_name)
                    scenarios.append(scenario)

    return scenarios