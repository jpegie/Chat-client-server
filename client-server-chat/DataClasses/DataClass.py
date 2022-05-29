from DataClasses.FIleDescriptor import FileDescriptor


class File:
    descriptor = FileDescriptor()
    binary = []

    end = False
    start = False
    blocks_amount = 0
    block_index = -1

    __gap = bytearray([])

    def __init__(self, binary=None, descriptor=None, block_index=-1, start=False, end=False, blocks_amount=0):
        if (binary is not None) and (descriptor is not None):
            self.binary = binary
            self.descriptor = descriptor
            self.block_index = block_index
            self.start = start
            self.end = end
            self.blocks_amount = blocks_amount

    def set_gap(self, gap_size):
        self.__gap = bytearray([1]*gap_size)


class ConnectingInfo:
    sender_name = ''
    message = []

    def __init__(self, sender_name='', message=None):
        self.sender_name = sender_name
        if message is not None:
            self.message = message


class Data:
    sender_name = ''
    receiver_name = ''
    message = ''

    def __init__(self, sender_name='', receiver_name='', message=''):
        self.message = message
        self.sender_name = sender_name
        self.receiver_name = receiver_name

