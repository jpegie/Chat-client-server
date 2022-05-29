import math
import pickle
import random
import socket
import threading
from PyQt5 import QtWidgets
import pathlib

from DataClasses.DataClass import Data, File, ConnectingInfo
from DataClasses.FIleDescriptor import FileDescriptor

UDP_MAX_SIZE = 65535  # max is 65535, but header is 8 bytes
UDP_MAX_SEND_SIZE = 60000
UDP_MAX_RECEIVE_SIZE = 65535

SERVER_PORT = 6965


class Client:
    name = ''
    port = 6969
    host = 'host'

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_addr = ('255.255.255.255', SERVER_PORT)

    chat = QtWidgets.QListWidget
    conn_button = QtWidgets.QPushButton
    login_tb = QtWidgets.QTextEdit

    attached_file = ''
    folder_for_saving = ''

    def __init__(self):
        self.port = random.randint(6000, 10000)
        self.host = socket.gethostbyname(socket.gethostname())

    def set_connect_button(self, button):
        self.conn_button = button

    def set_login_tb(self, tb):
        self.login_tb = tb

    def set_chat(self, chat_list_widget):
        self.chat = chat_list_widget

    def split_list(self, alist, wanted_parts=1, part_max_capacity=UDP_MAX_SEND_SIZE):
        return [alist[i * part_max_capacity: (i + 1) * part_max_capacity]
                for i in range(wanted_parts)]

    def connect(self, name):
        self.name = name
        self.client_socket.bind((self.host, self.port))
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while True:
            pickled_data = pickle.dumps(ConnectingInfo(sender_name=self.name))
            self.server_socket.sendto(pickled_data, self.server_addr)
            bin_data, server = self.server_socket.recvfrom(UDP_MAX_SIZE)
            data = pickle.loads(bin_data)
            if data.message.decode('UTF-8') == 'pfg_ip_response_serv':
                print('Received confirmation')
                print(f"Server ip:{str(server[0])}, port: {str(server[1])}")
                if data:
                    self.chat.addItem(f"🔴 {data.sender_name}: ip:{str(server[0])}, port: {str(server[1])}")
                self.server_addr = server
                break
            else:
                print('Verification failed')
            print('Trying again...')
        self.conn_button.setEnabled(False)
        self.login_tb.setEnabled(False)

    def send(self, message='', receiver=''):

        # To send a file:
        # 1. Create descriptor
        # 2. Send descriptor to the server
        # 3. Split pickled_data to blocks by UDP_MAX_SIZE bytes
        # 4. Send each block
        # During getting files server should save them by descriptor
        # Should contain that staff in dictionary

        if self.attached_file != '':

            file_name = pathlib.Path(self.attached_file).name.split(".")[0]
            file_extension = pathlib.Path(self.attached_file).suffix
            file_binary = open(self.attached_file, "rb").read()
            file_descriptor = FileDescriptor(file_name=file_name,
                                             file_extension=file_extension,
                                             sender_name=self.name,
                                             receiver_name=str(receiver))

            msg = Data(sender_name=self.name,
                       receiver_name=str(receiver),
                       message=f"Sent file {file_name}{file_extension} "
                               f"[{int(len(file_binary)/1024/1024)} mb]. Wait for downloading...")
            self.__send_message(msg)

            blocks_amount = math.ceil(len(file_binary) / UDP_MAX_SEND_SIZE)  # UDP_MAX_SIZE
            if blocks_amount > 1:
                blocks = self.split_list(file_binary, blocks_amount + 1)
                for i in range(0, blocks_amount):
                    attached_file = File(binary=blocks[i],
                                         descriptor=file_descriptor,
                                         block_index=i,
                                         start=True if i == 0 else False,
                                         end=True if i + 1 == blocks_amount else False,
                                         blocks_amount=blocks_amount)
                    self.__send_file(attached_file)
            else:
                attached_file = File(binary=file_binary,
                                     descriptor=file_descriptor,
                                     start=True,
                                     end=True,
                                     blocks_amount=1)
                self.__send_file(attached_file)
                # self.__send_file(attached_file)
        else:
            msg = Data(sender_name=self.name, receiver_name=str(receiver), message=message)
            self.__send_message(msg)
        # self.attached_file = ''

    def __send_message(self, message):
        pickled_data = pickle.dumps(message)
        self.server_socket.sendto(pickled_data, self.server_addr)

    def __send_file(self, file):
        pickled_data = pickle.dumps(file)
        self.server_socket.sendto(pickled_data, self.server_addr)

    def listen(self):
        threading.Thread(target=self._listen, daemon=True).start()

    def __key_to_sort(self, elem):
        return elem.block_index

    def __save_file(self, descriptor, blocks):  # descriptor is FileDescriptor, blocks is array of File
        blocks.sort(key=self.__key_to_sort)
        whole_file = []
        for i in range(0, len(blocks)):
            whole_file.append(blocks[i].binary)
        with open(f"{self.folder_for_saving}/{descriptor.file_name}{descriptor.file_extension}", "wb") as f:
            for block in whole_file:
                f.write(block)
        self.chat.addItem(f"🟢 {descriptor.file_name}{descriptor.file_extension} is saved")

    def __check_desc_is_dict(self, dict_, desc):
        for key in dict_.keys():
            if key.sender_name == desc.sender_name and \
                    key.receiver_name == desc.receiver_name and \
                    key.file_name == desc.file_name and \
                    key.file_extension == desc.file_extension:
                return key
        return None

    def _listen(self):
        current_getting_files = {}  # descriptor : array of File (need to save every block to row them up correctly)

        while True:
            bin_data, addr = self.server_socket.recvfrom(UDP_MAX_RECEIVE_SIZE)
            if not bin_data:
                continue
            else:
                try:
                    data = pickle.loads(bin_data)
                except:
                    continue
                if type(data) is File:
                    data_desc = self.__check_desc_is_dict(current_getting_files, data.descriptor)
                    if data_desc is not None:
                        current_getting_files[data_desc].append(data)
                    else:
                        current_getting_files[data.descriptor] = [data]

                    if data_desc is not None and len(current_getting_files[data_desc]) == data.blocks_amount:
                        self.__save_file(data_desc, current_getting_files[data_desc])
                        current_getting_files.pop(data_desc)
                    elif data_desc is None and len(current_getting_files[data.descriptor]) == data.blocks_amount:
                        self.__save_file(data.descriptor, current_getting_files[data.descriptor])

                elif type(data) is Data:
                    # if len(data.attached_file.binary) > 0:
                    #     self.chat.addItem(f"🔴 {data.sender_name}: {data.message.decode('utf-8')} / attached file: " +
                    #                       f"{data.attached_file.name}{data.attached_file.extension}")
                    #     self.chat.addItem(f"🟢 {data.attached_file.name}{data.attached_file.extension} is saved")
                    #     with open(f"{self.folder_for_saving}/{data.attached_file.name}{data.attached_file.extension}", "wb") as f:
                    #         f.write(data.attached_file.binary)
                    # else:
                    self.chat.addItem(f"🔴 {data.sender_name}: {data.message}")
