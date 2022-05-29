from DataClasses.Common.FileDescriptor import FileDescriptor


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
