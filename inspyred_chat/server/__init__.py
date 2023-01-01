#  Copyright (c) 2023. Inspyre Softworks

# class Server:
# 
#     def __init__(self, config):
#         self.config = config
# 
#     def broadcast(self, message):
#         pass
# 


import socket

from inspy_logger import InspyLogger

isl = InspyLogger('ChatServer', 'debug')

if not isl.device.started:
    root_logger = isl.device.start()


class Server:
    default_port = 7676
    default_bind_host = ''
    __cls_logger = None

    def __init__(self, bind_host: str = None, port: int = None):

        self.__cls_logger = isl.device.add_child()

        self.__bound = False

        self.__bind_host = bind_host or self.default_bind_host

        self.__port = port or self.default_port

        self.__socket = None

    @property
    def bind_host(self):
        return self.__bind_host

    @bind_host.setter
    def bind_host(self, new: str):
        if not isinstance(new, (str, None)):
            raise TypeError('bind_host must be a string')

        if self.bound:
            return

        self.__bind_host = new

    @property
    def bound(self):
        return self.__bound

    @bound.setter
    def bound(self, new):
        if isinstance(new, bool):
            self.__bound = new
        else:
            raise TypeError("'bound' must be of type 'bool'")

    @property
    def log(self):

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, new):
        if not isinstance(new, int):
            raise TypeError('port must be an integer')

        if not self.bound:
            self.__port = new

    @property
    def socket(self):
        if not self.__socket:
            self.__socket = socket.socket()

        return self.__socket

    def bind(self):
        if self.bound:
            return

        self.__socket.bind((self.__bind_host, self.__port))
