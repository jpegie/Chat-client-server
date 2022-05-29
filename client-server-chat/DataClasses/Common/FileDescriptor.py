class FileDescriptor:
    sender_name = ''
    receiver_name = ''
    file_name = ''
    file_extension = ''

    def __init__(self, file_name='', file_extension='', sender_name='', receiver_name=''):
        self.file_name = file_name
        self.file_extension = file_extension
        self.sender_name = sender_name
        self.receiver_name = receiver_name


