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
DELAY_TO_SEND_FILE = 0.0015
TCP_PORT_DIFF = 51


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

    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock_tcp.bind((host, port + TCP_PORT_DIFF))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    users = {}  # dict of name: sock
    users_locker = threading.Lock()

    def __init__(self):
        self.sock_tcp.listen()
        self.listen_to_new_users()

    def listen_to_new_users(self):
        threading.Thread(target=self.__listen_to_new_users).start()
        threading.Thread(target=self.__listen_for_tcp_clients).start()

    def send_message(self, data, receiver=None):

        if receiver is not None:
            pickled_data = pickle.dumps(data)
            receiver.send(pickled_data)
        else:
            receiver_name = data.receiver_name
            sender_name = data.sender_name

            if (type(data) is SimpleMessage) and (receiver_name in self.users) and (sender_name in self.users):
                pickled_data = pickle.dumps(data)
                self.users[sender_name].send(pickled_data)
                self.users[receiver_name].send(pickled_data)
            elif receiver_name in self.users:
                pickled_data = pickle.dumps(data)
                self.users[receiver_name].send(pickled_data)

    def notify_about_new_user(self, user):
        data = SimpleMessage(sender_name="s", message=f"Welcome {user} to this chat!")
        all_users_data = CurrentUsers(users=list(self.users.keys()))

        for u in self.users.keys():
            data.receiver_name = u
            all_users_data.receiver_name = u
            self.send_message(data)
            self.send_message(all_users_data)

    def notify_about_current_users(self):
        list_of_users = []
        for usr in self.users.keys():
            list_of_users.append(str(usr))
        for u in self.users:
            self.send_message(CurrentUsers(receiver_name=str(u), users=list_of_users), receiver=self.users[u])

    def send_file(self, file_key, files):
        blocks = files[file_key]

        receiver_name = file_key.receiver_name
        sender_name = file_key.sender_name

        if (receiver_name in self.users) and (sender_name in self.users):
            print(f"Blocks to send = {len(blocks)}")
            for block_key in blocks.keys():
                pickled_data = pickle.dumps(blocks[block_key])
                self.users[receiver_name].send(pickled_data)
                time.sleep(DELAY_TO_SEND_FILE)  # THE WORST WAY NOT TO LOSE DATA

            files.pop(file_key)

            message = SimpleMessage(
                message=f'File {file_key.file_name}{file_key.file_extension} delivered to {file_key.receiver_name}',
                sender_name='s',
                receiver_name=file_key.receiver_name)
            pickled_message = pickle.dumps(message)
            self.users[sender_name].send(pickled_message)

    def is_username_unique(self, name):
        if name in self.users.keys():
            return False
        return True

    def __listen_to_client(self, client, client_name):

        files = {}  # descriptors : [] array of File - blocks of real file

        while True:
            binary_message = client.recv(UDP_MAX_SIZE)
            if not binary_message:
                continue
            else:
                try:
                    message = pickle.loads(binary_message)
                except Exception as e:
                    print(str(e))
                    continue

                if type(message) is SimpleMessage:
                    self.send_message(message)
                elif type(message) is File:
                    file_desc = message.descriptor
                    file_key = get_equal_dict_key(files, file_desc)

                    if file_key is not None:
                        files[file_key][message.block_index] = message
                        # print(f"current blocks: {len(files[file_key])}, {message.blocks_amount} is needed")
                    else:
                        self.send_message(SimpleMessage(sender_name='s',
                                                        receiver_name=message.descriptor.sender_name,
                                                        message=f"File {message.descriptor.file_name}"
                                                                f"{message.descriptor.file_extension} "
                                                                f"is uploading to server"))
                        file_key = file_desc
                        files[file_key] = {}
                        files[file_key][message.block_index] = message

                    if len(files[file_key]) == message.blocks_amount:
                        self.send_message(SimpleMessage(sender_name='s',
                                                        receiver_name=message.descriptor.sender_name,
                                                        message=f"File {message.descriptor.file_name}"
                                                                f"{message.descriptor.file_extension} "
                                                                f"is uploaded to server"))
                        threading.Thread(target=self.send_file, args=(file_key, files,)).start()

    def __process_new_client(self, client):
        request_for_nickname = SimpleMessage(sender_name='s', message="RequestFromServerForNickname")
        self.send_message(request_for_nickname, client)
        binary_message = client.recv(UDP_MAX_SIZE)
        request = pickle.loads(binary_message)  # is SimpleMessage

        self.users_locker.acquire(True)

        if request.sender_name not in self.users:
            self.users[request.sender_name] = client
            self.notify_about_new_user(request.sender_name)
            # self.notify_about_current_users()
            threading.Thread(target=self.__listen_to_client, args=(client, request.sender_name,)).start()

        self.users_locker.release()

    def __listen_for_tcp_clients(self):
        while True:
            client, addr = self.sock_tcp.accept()
            threading.Thread(target=self.__process_new_client, args=(client, )).start()

    def __listen_to_new_users(self):
        print(f'Listening at {self.host} : {self.port}')

        while True:
            binary_message, addr = self.sock.recvfrom(UDP_MAX_SIZE)
            if not binary_message:
                continue
            else:
                try:
                    message = pickle.loads(binary_message)
                except Exception as e:
                    print(str(e))
                    continue

                if type(message) is ConnectionRequest:
                    if not self.is_username_unique(message.sender_name):
                        self.sock.sendto(pickle.dumps(SimpleMessage(sender_name='s',
                                                                    receiver_name=message.sender_name,
                                                                    message=f"User with name {message.sender_name} "
                                                                    f"already exists!")), addr)
                    else:
                        self.sock.sendto(pickle.dumps(SimpleMessage(sender_name='s',
                                                                    receiver_name=message.sender_name,
                                                                    message='pfg_ip_response_serv')), addr)

                        # self.notify_about_new_user(new_user)
                        # self.notify_about_current_users()

