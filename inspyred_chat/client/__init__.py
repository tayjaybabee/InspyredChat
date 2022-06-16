import socket
import threading

from inspyred_chat.client.commands import CMD_PREFIX, valid_commands

from uuid import uuid4
import uuid

UUID = uuid4()

# nick = input('Please choose a nickname: ')


class Client:
    def __init__(self, addr, port, nick=None):

        self._nick = input('Please choose a nickname: ') if nick is None else nick
        self.addr = addr
        self.port = port

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.addr, self.port))

        self.start_connection()

    def disconnect(self):
        self.client.close()

    def start_connection(self):
        recv_thread = threading.Thread(target=self.receive)
        recv_thread.start()

        write_thread = threading.Thread(target=self.write())
        write_thread.start()

    @property
    def nickname(self):
        return self._nick

    @nickname.setter
    def nickname(self, new_nickname):
        self.write()
        self._nick = new_nickname

    def receive(self):
        while True:
            try:
                msg = self.client.recv(1024).decode('ascii')
                if msg == 'REQ NICK':
                    self.client.send(self.nickname.encode('ascii'))
                elif msg == 'REQ UUID':
                    self.client.send(str(UUID).encode('ascii'))
                else:
                    print(msg)
            except:
                print('An unknown error occurred')
                self.client.close()
                break

    def write(self):
        while True:
            msg = input("")
            vc = valid_commands
            if not msg.startswith('/'):
                self.client.send(msg.encode('ascii'))
            else:
                cmd = msg.replace('/', '').lower()
                if cmd in vc.keys():
                    vc[cmd]['func'](self.client)
                    if cmd == 'disconnect':
                        break
                else:
                    print('Unknown command!')


chat_client = Client('192.168.2.145', 5300)
client = chat_client.client

# def receive():
#     while True:
#         try:
#             msg = client.recv(1024).decode('ascii')
#             if msg == 'REQ NICK':
#                 client.send(nick.encode('ascii'))
#             else:
#                 print(msg)
#         except:
#             print('An unknown error occurred')
#             client.close()
#             break
#
#
# def write():
#     while True:
#         msg = f'{nick}: {input("")}'
#         client.send(msg.encode('ascii'))
