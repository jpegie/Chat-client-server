class SimpleMessage:
    sender_name = ''
    receiver_name = ''
    message = ''

    def __init__(self, sender_name='', receiver_name='', message=''):
        self.message = message
        self.sender_name = sender_name
        self.receiver_name = receiver_name

