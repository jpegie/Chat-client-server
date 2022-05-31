class CurrentUsers:
    users = []
    receiver_name = ''
    sender_name = 's'

    def __init__(self, users=None, receiver_name=''):
        if users:
            self.users = users
            self.receiver_name = receiver_name
