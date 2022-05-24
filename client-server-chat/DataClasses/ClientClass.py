import pickle
import random
import socket
import threading
from PyQt5 import QtWidgets
import pathlib

from DataClasses.DataClass import Data, File


class Client:
    UDP_MAX_SIZE = 65535
    name = ''
    port = 6969
    host = 'host'
    server_addr = ('255.255.255.255', 6969)
    # server_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

    def split_list(self, alist, wanted_parts=1):
        length = len(alist)
        return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts]
                for i in range(wanted_parts)]

    def connect(self, name):
        self.name = name
        self.client_socket.bind((self.host, self.port))
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while True:
            # Send data
            pickled_data = pickle.dumps(Data(sender_name=self.name, receiver_name='', message=''))
            self.server_socket.sendto(pickled_data, self.server_addr)
            bin_data, server = self.server_socket.recvfrom(self.UDP_MAX_SIZE)
            data = pickle.loads(bin_data)
            if data.message.decode('UTF-8') == 'pfg_ip_response_serv':
                print('Received confirmation')
                print(f"Server ip:{str(server[0])}, port: {str(server[1])}")
                if data:
                    self.chat.addItem(f"🔴 {data.sender_name}: ip:{str(server[0])}, port: {str(server[1])}")
                server_addr = server
                break
            else:
                print('Verification failed')
            print('Trying again...')
        self.conn_button.setEnabled(False)
        self.login_tb.setEnabled(False)

    def send(self, message='', receiver=''):

        attached_file = File()
        if self.attached_file != '':
            file_name = pathlib.Path(self.attached_file).name.split(".")[0]
            file_extension = pathlib.Path(self.attached_file).suffix
            file_binary = open(self.attached_file, "rb").read()
            attached_file = File(name=file_name, extension=file_extension, binary=file_binary)
        data_to_send = Data(sender_name=self.name,
                            message=str(message).encode(),
                            receiver_name=str(receiver),
                            file=attached_file)
        pickled_data = pickle.dumps(data_to_send)

        # TODO: make to send files more that 60 mib
        if len(pickled_data) > self.UDP_MAX_SIZE:
            bin_parts = self.split_list(pickled_data, len(pickled_data)/(self.UDP_MAX_SIZE + 1))
            for i in range(0, len(bin_parts)):
                self.server_socket.sendto(bin_parts[i], self.server_addr)
        else:
            self.server_socket.sendto(pickled_data, self.server_addr)
        self.attached_file = ''

    def listen(self):
        threading.Thread(target=self._listen).start()

    def _listen(self):
        while True:
            bin_data, addr = self.server_socket.recvfrom(self.UDP_MAX_SIZE)  # try to decode data to str
            if not bin_data:
                continue
            else:
                try:
                    data = pickle.loads(bin_data)
                except:
                    continue

                if len(data.attached_file.binary) > 0:
                    self.chat.addItem(f"🔴 {data.sender_name}: {data.message.decode('utf-8')} / attached file: " +
                                      f"{data.attached_file.name}{data.attached_file.extension}")
                    self.chat.addItem(f"🟢 {data.attached_file.name}{data.attached_file.extension} is saved")
                    with open(f"{self.folder_for_saving}/{data.attached_file.name}{data.attached_file.extension}", "wb") as f:
                        f.write(data.attached_file.binary)
                else:
                    self.chat.addItem(f"🔴 {data.sender_name}: {data.message.decode('utf-8')}")
                print(f"New message! From: {data.sender_name} Message: {data.message.decode('utf-8')}")
                #self.app.add_message_to_view(data)

