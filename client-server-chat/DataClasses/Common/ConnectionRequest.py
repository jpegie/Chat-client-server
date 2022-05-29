class ConnectionRequest:
    sender_name = ''
    message = []

    def __init__(self, sender_name='', message=None):
        self.sender_name = sender_name
        if message is not None:
            self.message = message