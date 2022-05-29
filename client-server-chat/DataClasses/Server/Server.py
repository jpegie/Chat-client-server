import socket
import pickle
import threading
import time

from DataClasses.Common.SimpleMessage import SimpleMessage
from DataClasses.Common.File import File
from DataClasses.Common.ConnectionRequest import ConnectionRequest
from DataClasses.Common.User import User
from DataClasses.Common.CurrentUsers import CurrentUsers

UDP_MAX_SIZE = 65535
DELAY_TO_SEND_FILE = 0.001


def first(iterable, default=None):
    for item in iterable:
        return item
    return default


def get_equal_dict_key(dict_, desc):
    for key in dict_.keys():
        if key.sender_name == desc.sender_name and \
                key.receiver_name == desc.receiver_name and \
                key.file_name == desc.file_name and \
                key.file_extension == desc.file_extension:
            return key
    return None


def key_to_sort(elem):
    return elem.block_index


class Server:
    host = ''
    port = 6965

    users = []

    def __init__(self):
        self.listen()

    def listen(self):
        threading.Thread(target=self.__listen).start()

    def send_message(self, data, sock):
        receiver = first(x for x in self.users if x.name == data.receiver_name)
        sender = first(x for x in self.users if x.name == data.sender_name)
        if type(data) is SimpleMessage and receiver is None and sender is not None:
            data.sender_name = 's'
            data.message = f'No user such as {data.receiver_name}'
            pickled_data = pickle.dumps(data)
            sock.sendto(pickled_data, sender.address)
        elif type(data) is SimpleMessage and receiver is not None and sender is not None:
            pickled_data = pickle.dumps(data)
            sock.sendto(pickled_data, sender.address)
            sock.sendto(pickled_data, receiver.address)
        elif receiver is not None:
            pickled_data = pickle.dumps(data)
            sock.sendto(pickled_data, receiver.address)

    def notify_about_new_user(self, user, sock):
        data = SimpleMessage(sender_name="s", message=f"Welcome {user.name} to this chat!")
        for u in self.users:
            data.receiver_name = u.name
            self.send_message(data, sock)

    def notify_about_current_users(self, sock):
        for u in self.users:
            self.send_message(CurrentUsers(receiver_name=u.name, users=self.users), sock)
            self.send_message(SimpleMessage(sender_name='s',
                                            receiver_name=u.name,
                                            message=("Current users: " +
                                                     ", ".join(m.name for m in self.users))), sock)

    def __send_file(self, file_key, files, sock):
        blocks = files[file_key]
        receiver = first(x for x in self.users if x.name == file_key.receiver_name)
        sender = first(x for x in self.users if x.name == file_key.sender_name)

        if sender is not None and receiver is not None:
            print(f"Blocks to send = {len(blocks)}")
            for block_key in blocks.keys():
                pickled_data = pickle.dumps(blocks[block_key])
                sock.sendto(pickled_data, receiver.address)
                time.sleep(DELAY_TO_SEND_FILE)  # THE WORST WAY NOT TO LOSE DATA

            files.pop(file_key)

            message = SimpleMessage(
                message=f'File {file_key.file_name}{file_key.file_extension} delivered to {file_key.receiver_name}',
                sender_name='s',
                receiver_name=file_key.receiver_name)
            pickled_message = pickle.dumps(message)
            sock.sendto(pickled_message, sender.address)

    def __is_username_unique(self, name):
        for user in self.users:
            if user.name == name:
                return False
        return True

    def __listen(self):

        files = {}  # descriptors : [] array of File - blocks of real file

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((self.host, self.port))

        print(f'Listening at {self.host} : {self.port}')

        while True:
            bin_data, addr = server_socket.recvfrom(UDP_MAX_SIZE)
            if not bin_data:
                continue
            else:
                try:
                    data = pickle.loads(bin_data)
                except Exception as e:
                    print(str(e))
                    continue

                if type(data) is ConnectionRequest:
                    if not self.__is_username_unique(data.sender_name):
                        server_socket.sendto(pickle.dumps(SimpleMessage(sender_name='s',
                                                                        receiver_name=data.sender_name,
                                                                        message=f"User with name {data.sender_name} "
                                                                                f"already exists!")), addr)
                    else:
                        new_user = User(address=addr, name=data.sender_name)
                        self.users.append(new_user)
                        self.send_message(SimpleMessage(sender_name='s',
                                                        receiver_name=data.sender_name,
                                                        message='pfg_ip_response_serv'), server_socket)
                        self.notify_about_new_user(new_user, server_socket)
                        self.notify_about_current_users(server_socket)
                elif type(data) is SimpleMessage:
                    self.send_message(data, server_socket)
                elif type(data) is File:
                    file_desc = data.descriptor
                    file_key = get_equal_dict_key(files, file_desc)

                    if file_key is not None:
                        files[file_key][data.block_index] = data
                        # print(f"current blocks: {len(files[file_key])}, {data.blocks_amount} is needed")
                    else:
                        self.send_message(SimpleMessage(sender_name='s',
                                                        receiver_name=data.descriptor.sender_name,
                                                        message=f"File {data.descriptor.file_name}"
                                                                f"{data.descriptor.file_extension} "
                                                                f"is uploading to server"), server_socket)
                        file_key = file_desc
                        files[file_key] = {}
                        files[file_key][data.block_index] = data

                    if len(files[file_key]) == data.blocks_amount:
                        self.send_message(SimpleMessage(sender_name='s',
                                                        receiver_name=data.descriptor.sender_name,
                                                        message=f"File {data.descriptor.file_name}"
                                                                f"{data.descriptor.file_extension} "
                                                                f"is uploaded to server"), server_socket)
                        threading.Thread(target=self.__send_file, args=(file_key, files, server_socket,)).start()
