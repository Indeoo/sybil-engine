import json

from loguru import logger


def load_file_rows(path):
    with open(path, "r") as f:
        logger.info(f"Reading {path}")
        return [row.strip() for row in f]


import os


def load_abi(path):
    try:
        absolute_path = os.path.join(os.path.dirname(__file__), path)
        with open(absolute_path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"No file found at {path}")
        return None



def load_json_resource(path):
    with open(f"resources/{path}", "r") as file:
        return json.load(file)
