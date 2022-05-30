import math
import pickle
import random
import socket
import threading
import time

from PyQt5 import QtWidgets
import pathlib

from DataClasses.Common.SimpleMessage import SimpleMessage
from DataClasses.Common.File import File
from DataClasses.Common.ConnectionRequest import ConnectionRequest
from DataClasses.Common.FileDescriptor import FileDescriptor
from DataClasses.Common.CurrentUsers import CurrentUsers

UDP_MAX_SIZE = 65535  # max is 65535, but header is 8 bytes
UDP_MAX_SEND_SIZE = 60000
UDP_MAX_RECEIVE_SIZE = UDP_MAX_SIZE

SERVER_PORT = 6965
DELAY_TO_SEND_FILE = 0.0015


def split_list(alist, wanted_parts=1, part_max_capacity=UDP_MAX_SEND_SIZE):
    return [alist[i * part_max_capacity: (i + 1) * part_max_capacity]
            for i in range(wanted_parts)]


def key_to_sort(elem):
    return elem.block_index


def get_equal_dict_key(dict_, desc):
    for key in dict_.keys():
        if key.sender_name == desc.sender_name and \
                key.receiver_name == desc.receiver_name and \
                key.file_name == desc.file_name and \
                key.file_extension == desc.file_extension:
            return key
    return None


class Client:
    name = ''
    port = 6969
    host = 'host'

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_addr = ('255.255.255.255', SERVER_PORT)

    ui_chat = QtWidgets.QListWidget
    ui_conn_button = QtWidgets.QPushButton
    ui_login = QtWidgets.QTextEdit
    ui_current_users = QtWidgets.QComboBox

    attached_file = ''
    folder_for_saving = ''

    def __init__(self):
        self.port = random.randint(6000, 10000)
        self.host = socket.gethostbyname(socket.gethostname())

        self.client_socket.bind((self.host, self.port))
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def set_ui_conn_button(self, button):
        self.ui_conn_button = button

    def set_ui_login(self, tb):
        self.ui_login = tb

    def set_ui_chat(self, chat_list_widget):
        self.ui_chat = chat_list_widget

    def set_ui_current_users(self, ui):
        self.ui_current_users = ui

    def connect(self, name):
        self.name = name
        pickled_data = pickle.dumps(ConnectionRequest(sender_name=self.name))
        self.server_socket.settimeout(5)

        try:
            self.server_socket.sendto(pickled_data, self.server_addr)
            binary_message, address = self.server_socket.recvfrom(1024)

            self.server_socket.settimeout(None)

            message = pickle.loads(binary_message)
            if message:
                if type(message) is SimpleMessage:
                    if message.message == 'pfg_ip_response_serv':
                        print(f"Server ip:{str(address[0])}, port: {str(address[1])}")
                        self.__add_message_to_chat(only_str=f"Connected to chat [{str(address[0])} : {str(address[1])}]")
                        self.server_addr = address
                        self.ui_conn_button.setEnabled(False)
                        self.ui_login.setEnabled(False)

                        self.listen()

                    else:
                        self.__add_message_to_chat(message)
                elif type(message) is CurrentUsers:
                    self.__update_users(message.users)
        except Exception as e:
            print(str(e))

    def __send_file(self, receiver=''):

        file_name = pathlib.Path(self.attached_file).name.split(".")[0]
        file_extension = pathlib.Path(self.attached_file).suffix
        file_binary = open(self.attached_file, "rb").read()
        file_descriptor = FileDescriptor(file_name=file_name,
                                         file_extension=file_extension,
                                         sender_name=self.name,
                                         receiver_name=str(receiver))

        msg = SimpleMessage(sender_name=self.name,
                            receiver_name=str(receiver),
                            message=f"Sending file {file_name}{file_extension} "
                                    f"[{int(len(file_binary) / 1024 / 1024)} mib] to {receiver}")
        self.send_message(msg)

        blocks_amount = math.ceil(len(file_binary) / UDP_MAX_SEND_SIZE)  # UDP_MAX_SIZE
        if blocks_amount > 1:
            blocks = split_list(file_binary, blocks_amount)
            for i in range(0, blocks_amount):
                attached_file = File(binary=blocks[i],
                                     descriptor=file_descriptor,
                                     block_index=i,
                                     start=True if i == 0 else False,
                                     end=True if i + 1 == blocks_amount else False,
                                     blocks_amount=blocks_amount)
                self.send_file(attached_file)
                time.sleep(DELAY_TO_SEND_FILE)  # THE WORST WAY NOT TO LOSE DATA
        else:
            attached_file = File(binary=file_binary,
                                 descriptor=file_descriptor,
                                 start=True,
                                 end=True,
                                 blocks_amount=1)
            self.send_file(attached_file)
            time.sleep(DELAY_TO_SEND_FILE)  # THE WORST WAY NOT TO LOSE DATA

    def send(self, message='', receiver=''):

        # To send a file:
        # 1. Create descriptor
        # 2. Send descriptor to the server
        # 3. Split pickled_data to blocks by UDP_MAX_SIZE bytes
        # 4. Send each block
        # During getting files server should save them by descriptor
        # Should contain that staff in dictionary

        if message != '':
            msg = SimpleMessage(sender_name=self.name, receiver_name=str(receiver), message=message)
            self.send_message(msg)

        if self.attached_file != '':
            threading.Thread(target=self.__send_file, args=(receiver, )).start()

    def listen(self):
        threading.Thread(target=self.__listen, daemon=True).start()

    def send_message(self, message):
        pickled_data = pickle.dumps(message)
        self.server_socket.sendto(pickled_data, self.server_addr)

    def send_file(self, file):
        pickled_data = pickle.dumps(file)
        self.server_socket.sendto(pickled_data, self.server_addr)

    def save_file(self, descriptor, blocks_dict):  # descriptor is FileDescriptor, blocks is array of File
        blocks = []
        for block_key in blocks_dict.keys():
            blocks.append(blocks_dict[block_key])
        blocks.sort(key=key_to_sort)
        with open(f"{self.folder_for_saving}/{descriptor.file_name}{descriptor.file_extension}", "wb") as f:
            for block in blocks:
                f.write(block.binary)
        self.ui_chat.addItem(f"🟢 {descriptor.file_name}{descriptor.file_extension} is saved")

    def __add_message_to_chat(self, message=None, only_str=''):
        if only_str != '' and message is None:
            self.ui_chat.addItem(f"🔴 {only_str}")
        elif message is not None:
            self.ui_chat.addItem(f"🔴 {message.sender_name + ': ' if message.sender_name != 's' else ''}{message.message}")

    def __update_users(self, users):
        self.ui_current_users.clear()
        for user in users:
            if user.name != self.name:
                self.ui_current_users.addItem(user.name)
        if self.ui_current_users.count() != 0:
            self.ui_current_users.setCurrentIndex(0)

    def __listen(self):
        current_getting_files = {}  # descriptor : {block_index : block_data}
        while True:
            bin_data, addr = self.server_socket.recvfrom(UDP_MAX_RECEIVE_SIZE)
            if not bin_data:
                continue
            else:
                try:
                    message = pickle.loads(bin_data)
                except:
                    continue
                if type(message) is File:
                    file_key = get_equal_dict_key(current_getting_files, message.descriptor)
                    if file_key is not None:
                        current_getting_files[file_key][message.block_index] = message
                        print(f'got blocks: {len(current_getting_files[file_key])}/{message.blocks_amount}')
                    else:
                        file_key = message.descriptor
                        current_getting_files[file_key] = {}
                        current_getting_files[file_key][message.block_index] = message

                    if len(current_getting_files[file_key]) == message.blocks_amount:
                        self.save_file(file_key, current_getting_files[file_key])

                elif type(message) is SimpleMessage:
                    self.__add_message_to_chat(message)

                elif type(message) is CurrentUsers:
                    self.__update_users(message.users)
