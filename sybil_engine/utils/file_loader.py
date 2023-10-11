import json

from loguru import logger


def load_file_rows(path):
    with open(path, "r") as f:
        logger.info(f"Reading {path}")
        return [row.strip() for row in f]


def load_abi(path):
    with open(path) as f:
        return f.read()


def load_json_resource(path):
    with open(f"resources/{path}", "r") as file:
        return json.load(file)
