class File:
    name = ''
    extension = ''
    binary = []

    def __init__(self,
                 binary=None,
                 blocks_amount=0,
                 name='', extension=''):
        if binary is not None:
            self.binary = binary
            self.name = name
            self.extension = extension
            self.blocks_amount = blocks_amount

