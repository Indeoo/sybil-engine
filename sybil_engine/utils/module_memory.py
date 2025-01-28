memory = {

}


def add_memory_list(key, value):
    memory[key] = value


def accumulate_by_key(key, value):
    if key in memory:
        memory[key] += value
    else:
        memory[key] = [value]


def remove_key(key):
    del memory[key]


def get_by_key(key):
    return memory.get(key)
