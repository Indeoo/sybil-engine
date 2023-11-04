class AccountStorage:

    def __init__(self):
        self.storage = {}

    def put(self, key, value):
        self.storage[key] = value

    def get(self, key):
        return self.storage.get(key)