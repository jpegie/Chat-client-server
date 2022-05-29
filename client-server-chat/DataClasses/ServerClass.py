import socket
import pickle
import threading
import time

from DataClasses.DataClass import Data, File, ConnectingInfo
from DataClasses.MemberClass import Member


def first(iterable, default=None):
    for item in iterable:
        return item
    return default


UDP_MAX_SIZE = 65535


class Server:
    host = ''
    port = 6965

    members = []

    def __init__(self):
        self.listen()

    def send_message(self, data, sock):
        receiver = first(x for x in self.members if x.name == data.receiver_name)
        sender = first(x for x in self.members if x.name == data.sender_name)
        if type(data) is Data and receiver is None and sender is not None:
            data.sender_name = 's'
            data.message = f'No member such as {data.receiver_name}'
            pickled_data = pickle.dumps(data)
            sock.sendto(pickled_data, sender.address)
        elif type(data) is Data and receiver is not None and sender is not None:
            pickled_data = pickle.dumps(data)
            sock.sendto(pickled_data, sender.address)
            sock.sendto(pickled_data, receiver.address)
        elif receiver is not None:
            pickled_data = pickle.dumps(data)
            sock.sendto(pickled_data, receiver.address)

    def new_member(self, member, sock):
        data = Data(sender_name="s", message=f"Welcome {member.name} to this chat!".encode())
        for m in self.members:
            data.receiver_name = m.name
            self.send_message(data, sock)

    def listen(self):
        threading.Thread(target=self._listen).start()

    def __key_to_sort(self, elem):
        return elem.block_index

    def __send_file(self, descriptor, blocks, sock):
        # blocks.sort(key=self.__key_to_sort)
        receiver = first(x for x in self.members if x.name == descriptor.receiver_name)
        sender = first(x for x in self.members if x.name == descriptor.sender_name)

        if sender is not None and receiver is not None:
            print(f"Blocks to send = {len(blocks)}")
            for block in blocks:
                pickled_data = pickle.dumps(block)
                sock.sendto(pickled_data, receiver.address)
                # time.sleep(0.01)

            message = Data(
                message=f'File {descriptor.file_name}{descriptor.receiver_name} delivered to {descriptor.sender_name}',
                sender_name=descriptor.sender_name,
                receiver_name=descriptor.receiver_name)
            pickled_message = pickle.dumps(message)
            sock.sendto(pickled_message, sender.address)

    def __check_desc_is_dict(self, dict_, desc):
        for key in dict_.keys():
            if key.sender_name == desc.sender_name and \
                    key.receiver_name == desc.receiver_name and \
                    key.file_name == desc.file_name and \
                    key.file_extension == desc.file_extension:
                return key
        return None

    def _listen(self):

        files = {}  # descriptors : [] array of File - blocks of real file

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((self.host, self.port))

        print(f'Listening at {self.host}:{self.port}')

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

                if type(data) is ConnectingInfo:
                    new_member = Member(address=addr, name=data.sender_name)
                    self.members.append(new_member)
                    self.send_message(Data(sender_name='s',
                                           receiver_name=data.sender_name,
                                           message='pfg_ip_response_serv'.encode()), server_socket)
                    self.send_message(Data(sender_name='s',
                                           receiver_name=data.sender_name,
                                           message=("Current members: " + ", ".join(str(m.name)
                                                                                    for m in self.members)).encode(
                                               'utf-8')), server_socket)
                    self.new_member(new_member, server_socket)
                elif type(data) is Data:
                    self.send_message(data, server_socket)
                elif type(data) is File:
                    file_desc = data.descriptor
                    file_ = self.__check_desc_is_dict(files, file_desc)
                    if file_ is not None:

                        already_got = False

                        files[file_].append(data)
                    else:
                        files[file_desc] = [data]
                    if file_ is None and len(files[file_desc]) == data.blocks_amount:
                        self.__send_file(file_desc, files[file_desc], server_socket)
                        files.pop(file_desc)
                    elif file_ is not None and len(files[file_]) == data.blocks_amount:
                        # threading.Thread(target=lambda: self.__send_file(file_, files[file_], server_socket)).start()
                        self.__send_file(file_, files[file_], server_socket)
                        files.pop(file_)
