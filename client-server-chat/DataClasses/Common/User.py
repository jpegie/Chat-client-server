class User:
    address = tuple[str, int]  # [ip, id]
    name = 'user'

    def __init__(self, address, name):
        self.address = address
        self.name = name
