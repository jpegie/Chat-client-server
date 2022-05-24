import socket
import pickle
import threading

from DataClasses.DataClass import Data
from DataClasses.MemberClass import Member


def first(iterable, default=None):
    for item in iterable:
        return item
    return default


class Server:
    UDP_MAX_SIZE = 65535
    host = ''
    port = 6969

    members = []

    def send_message(self, data, sock):
        receiver = first(x for x in self.members if x.name == data.receiver_name)
        if receiver is not None:
            pickled_data = pickle.dumps(data)

            sock.sendto(pickled_data, receiver.address)

    def new_member(self, member, sock):
        data = Data(sender_name="s", message=f"Welcome {member.name} to this chat!".encode())
        for m in self.members:
            data.receiver_name = m.name
            self.send_message(data, sock)

    def listen(self):
        threading.Thread(target=self._listen()).start()

    def _listen(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((self.host, self.port))

        print(f'Listening at {self.host}:{self.port}')

        while True:
            bin_data, addr = server_socket.recvfrom(self.UDP_MAX_SIZE)
            if not bin_data:
                continue
            else:
                try:
                    data = pickle.loads(bin_data)
                except:
                    continue

                if first(x for x in self.members if x.address == addr) is None:
                    new_member = Member(address=addr, name=data.sender_name)
                    self.members.append(new_member)
                    self.send_message(Data(sender_name='s',
                                           receiver_name=data.sender_name,
                                           message='pfg_ip_response_serv'.encode()), server_socket)
                    self.send_message(Data(sender_name='s',
                                           receiver_name=data.sender_name,
                                           message=("Current members: " + ", ".join(str(m.name)
                                                                                    for m in self.members)).encode('utf-8')), server_socket)
                    self.new_member(new_member, server_socket)
                else:
                    self.send_message(data, server_socket)
