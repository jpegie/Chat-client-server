import socket
import pickle
import threading
import time

from DataClasses.Common import FileDescriptor
from DataClasses.Common.SimpleMessage import SimpleMessage
from DataClasses.Common.File import File
from DataClasses.Common.ConnectionRequest import ConnectionRequest
from DataClasses.Common.User import User
from DataClasses.Common.CurrentUsers import CurrentUsers

UDP_MAX_SIZE = 65535
DELAY_TO_SEND_FILE = 0.000
TCP_PORT_DIFF = 51
PACKET_SIZE = 4096


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

    def __del__(self):
        try:
            self.sock_tcp.close()
            print("Socket closed successfully!")
        except Exception as e:
            print(str(e))
        finally:
            try:
                for u in self.users.keys():
                    self.users[u].close()
                print("Clients sockets closed successfully!")
            except Exception as e:
                print(str(e))

    def listen_to_new_users(self):
        threading.Thread(target=self.__listen_to_new_users, daemon=True).start()
        threading.Thread(target=self.__listen_for_tcp_clients, daemon=True).start()

    def send_message(self, data, file=None, receiver=None):

        if receiver is not None:
            pickled_data = pickle.dumps(data)
            receiver.send(pickled_data)
        else:
            receiver_name = data.receiver_name
            sender_name = data.sender_name

            if (file is not None) and (receiver_name in self.users):
                pickled_data = pickle.dumps(data)
                # pickled_file = pickle.dumps(file)
                self.users[receiver_name].send(pickled_data)
                time.sleep(1)
                self.users[receiver_name].sendall(file)
            else:
                try:
                    if (type(data) is SimpleMessage) and (receiver_name in self.users) and (sender_name in self.users):
                        pickled_data = pickle.dumps(data)
                        self.users[sender_name].send(pickled_data)
                        self.users[receiver_name].send(pickled_data)
                    elif receiver_name in self.users:
                        pickled_data = pickle.dumps(data)
                        self.users[receiver_name].send(pickled_data)
                except Exception as e:
                    print(str(e))

    def notify_about_new_user(self, user):
        data = SimpleMessage(sender_name="s", message=f"Welcome {user} to this chat!")

        for u in self.users.keys():
            data.receiver_name = u
            self.send_message(data=data)

    def notify_about_current_users(self):
        list_of_users = []
        for usr in self.users.keys():
            list_of_users.append(str(usr))
        for u in self.users:
            self.send_message(CurrentUsers(receiver_name=str(u), users=list_of_users), receiver=self.users[u])

    def is_username_unique(self, name):
        if name in self.users.keys():
            return False
        return True

    binary_message = bytes()

    def __listen_to_client(self, client, client_name):
        data = []
        while True:
            binary_message = client.recv(PACKET_SIZE)

            try:
                message = pickle.loads(binary_message)
            except Exception as e:
                print(str(e))
                continue
            if type(message) is SimpleMessage:
                if message.file_desc is not None:

                    # for i in range(0, message.file_desc.packets_amount):
                    #     data.append(client.recv(PACKET_SIZE))
                    try:
                        # file_binary = b''.join(data)
                        # incoming_file = pickle.loads(bytes(file_binary))
                        file_binary = client.recv(message.file_desc.packets_amount)
                        self.send_message(message, file=file_binary)
                    except Exception as e:
                        print(str(e))
                        continue
                    finally:
                        data = []
                else:
                    self.send_message(message)

    def __process_new_client(self, client):
        request_for_nickname = SimpleMessage(sender_name='s', message="RequestFromServerForNickname")
        self.send_message(request_for_nickname, receiver=client)
        binary_message = client.recv(UDP_MAX_SIZE)
        request = pickle.loads(binary_message)  # is SimpleMessage

        self.users_locker.acquire(True)
        if request.sender_name not in self.users:
            self.users[request.sender_name] = client
            self.notify_about_new_user(request.sender_name)
            self.notify_about_current_users()
            threading.Thread(target=self.__listen_to_client, args=(client, request.sender_name,)).start()

        self.users_locker.release()

    def __listen_for_tcp_clients(self):
        while True:
            client, addr = self.sock_tcp.accept()
            print(f"New client with addr: {addr}. {client}")
            threading.Thread(target=self.__process_new_client, args=(client,), daemon=True).start()

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
