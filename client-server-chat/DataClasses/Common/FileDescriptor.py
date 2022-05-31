class FileDescriptor:
    packets_amount = 1
    name = ''
    extension = 0

    def __init__(self, packets_amount=1, name = '', extension=''):
        self.packets_amount = packets_amount
        self.name = name
        self.extension = extension


