import inspect
import json

from loguru import logger


def load_file_rows(path):
    with open(path, "r") as f:
        logger.info(f"Reading {path}")
        return [row.strip() for row in f]


import os


def load_abi(path):
    try:
        # Get the absolute file path of the function that calls `load_abi`.
        caller_path = inspect.stack()[1].filename
        # Combine the caller's directory with the provided relative path.
        absolute_path = os.path.join(os.path.dirname(caller_path), path)
        with open(absolute_path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"No file found at {path}")
        return None




def load_json_resource(path):
    with open(f"resources/{path}", "r") as file:
        return json.load(file)
