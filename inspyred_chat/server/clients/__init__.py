#  Copyright (c) 2022. Inspyre Softworks
"""
Manage client connections and exchanges.
"""
from time import time
from uuid import uuid4

from inspyred_chat.server.logger import LOG_DEVICE


class Manifest(object):
    def __init__(self):
        self.__contents = {}
        self.add_entry()

    def add_entry(
            self,
            uuid_from_client,
            uuid_to_client,
            nickname,
            skip_save=False):
        """
        The add_entry function adds a new entry to the dictionary.

        Args:

            self:
                Access the attributes and methods of the class in python

            uuid_from_client (String):
               Store the uuid of the client that is requesting a friend request

            uuid_to_client (String):
                Store the uuid of the client that is being added to the list

            nickname (String):
                Store the nickname of the client that

            skip_save (bool)=False:
                Tell the function to not save the entry to device storage.

        Returns:
            The updated contents of the dictionary
        """
        entry = {
            uuid_to_client: {
                'uuid_from_client': uuid_from_client,
                'nickname': nickname,
                'created': time(),
                'status': None
            }
        }
        """
        Create a structure containing the fields for the new entry we want to add.
        """
        self.__contents.update(entry)

        return self.__contents.update()

    @property
    def contents(self):
        """
        The contents function returns a list dictionaries.

        Each of the dictionaries returned contains the following information for a connected client:
            * Unique ID provided by client
            * Unique ID provided by server to client
            * Client nickname
            * Time of entry creation
            *

        Args:

            self: Access the attributes and methods of the class

        Returns:
            The contents of the file as a string

        Doc Author:
            Trelent
        """
        return self.__contents or None


class Client(object):
    REQUEST_POINTERS = [
        'UUID',
        'NICK',
    ]

    def __init__(self, client_obj):
        self._CLASS_LOGNAME = 'InspyredChat.server.clients:Client'
        self.log = LOG_DEVICE.add_child(self._CLASS_LOGNAME)
        self.log.debug('Logger started!')
        self.client = client_obj
        self.nickname = None

        self.UUID = self.generate_UUID()
        self.client_UUID = None

    def handshake(self):
        """
        The handshake function is responsible for receiving the client's nickname
        and UUID.

        It is also responsible for sending the client's nickname and UUID to the
        server.

        Arguments:
            self: Access the attributes and methods of the class in python

        Returns:
            None
        """
        # ToDo:
        #    - [ ] Add a way to fail gracefully
        log = LOG_DEVICE.add_child(f'{self._CLASS_LOGNAME}.handshake')
        log.debug('Handshake started')

        log.debug('Requesting nickname from client')
        self.nickname = self.request('nick')
        log.debug(f'Received NICK: {self.nickname}')

        log.debug('Requesting UUID from client.')
        self.client_UUID = self.request('uuid')
        log.debug(f'Received UUID: {self.client_UUID}')

    def receive(self):
        """
        The 'receive' function is used to receive data from the client.
        It is called by the server when a new connection is made, and it will be
        called once for each message sent by the client.

        Args:
            self: Access the attributes and methods of the class

        Returns:
            The data received from the server

        Doc Author:
            Trelent
        """
        return self.client.recv(1024).decode('ascii')

    def send(self, message):
        """
        The send function sends a message to the client.


        Arguments:
            self:
                Reference the class instance
            message (String):
                Pass the message to send to the client.

        Returns:
            The number of bytes sent to the socket
        """
        self.client.send(message.encode('ascii'))

    def request(self, pointer):
        """
        The request function is used to request a specific pointer from the device.

        The function takes one parameter, which is the pointer you want to
        request. This function will return a string containing all the data for that
        pointer.

        Arguments:
            self:
                Access the class attributes and methods

            pointer:
                Specify which data is requested

        Returns:
            The value of the pointer
        """
        log = LOG_DEVICE.add_child(f'{self._CLASS_LOGNAME}.request')
        log.debug('Logger started!')
        pointer = pointer.upper()
        log.debug(f'Received pointer {pointer}')

        if pointer not in self.REQUEST_POINTERS:
            raise ValueError(
                f"The 'pointer' parameter must be one of; {', '.join(self.REQUEST_POINTERS)}. Not '{pointer}'.")

        self.send(f'REQ {pointer}')

        log.debug(f'Sent request for pointer; {pointer}')

        return self.receive()

    def generate_UUID(self):
        """
        The generate_UUID function generates a universally unique identifier for the
        current object.

        This UUID is generated using Python's uuid4() function, which creates a
        random UUID. The resulting UUID is then appended to the current object's
        UUID list and returned.

        Args:
            self: Refer to the object itself

        Returns:
            A string of a uuid

        Doc Author:
            Trelent
        """
        return str(uuid4())
