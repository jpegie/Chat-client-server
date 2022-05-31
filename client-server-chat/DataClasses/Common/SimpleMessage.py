from DataClasses.Common.FileDescriptor import FileDescriptor


class SimpleMessage:
    file_desc = FileDescriptor
    sender_name = ''
    receiver_name = ''
    message = ''

    def __init__(self, sender_name='', receiver_name='', message='', file_desc=None):
        self.message = message
        self.sender_name = sender_name
        self.receiver_name = receiver_name
        self.file_desc = file_desc

