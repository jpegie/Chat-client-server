class File:
    name = ''
    extension = ''
    binary = []

    def __init__(self, name='', extension='', binary=None):
        if (name != '') and (extension != '') and (binary is not None):
            self.name = name
            self.extension = extension
            self.binary = binary


class Data:
    sender_name = ''
    receiver_name = ''
    message = []
    attached_file = File()

    def __init__(self, sender_name='', receiver_name='', message=[], file=None):
        self.message = message
        self.sender_name = sender_name
        self.receiver_name = receiver_name
        if file is not None:
            self.attached_file = file
