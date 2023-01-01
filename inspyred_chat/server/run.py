#  Copyright (c) 2022. Inspyre Softworks

import socket
from threading import Thread
from uuid import uuid4

from inspyred_chat.server.cli import CLIArgs
from inspyred_chat.server.config import Config
from inspyred_chat.server.info import PROG
from inspyred_chat.server.logger import LOG_DEVICE

LOG = LOG_DEVICE.add_child(f'{PROG}.run')

CONFIG = Config()
_args = CLIArgs(CONFIG)

ARGS = _args.parsed
"""
The parsed arguments from invocation at the command-line.
"""

HOST = CONFIG.parser.get('USER', 'bind-addr')
"""
(str) - A string containing the hostname we want to bind our server to.

The hostname contained here is retrieved from the value contained in the 
configuration key 'bind-addr'. The program will look for a bind address to use in 
the 'USER' section (if it exists) of the config-file (if that exists). 

The default value the program will fallback to if not given a specific bind-address 
at any time is '127.0.0.1'. This address is not accessible from outside of the 
device hosting the chat server.

Note:
    If you want to be able to connect to this server from another computer 
    (either within or outside of your local network) you will need to provide the 
    appropriate bind-address.
    
        For example;
            - Want to only connect within your local network? Use your computer's 
            local IP address (Usually looks like; '192.168.*.*' or '10.*.*.*')
            
            - Want to connect from any computer on the internet? Use the IP 
            address that your modem is assigned by your ISP (your external IP 
            address).
            
                * Side Note:
                    You can easily find out your IP address using IP-Reveal from 
                    Inspyre Softworks. There are two versions easily installed via PIP:
                        * IP-Reveal:
                            The bigger of the two versions, as it sports a graphical user 
                            interface using PySimpleGUI.
                            
                            Install:
                                ```pip install ip-reveal```
                                
                        * IP-Reveal Headless:
                            Developed for headless machines where you can connect in
                            one form or another but still need an IP address. Also great 
                            for use on your computer if you don't need all the features of
                            the large GUI version.
                            
                            Links:
                                - (GitHub)[https://www.github.com/tayjaybabee/ip-reveal-headless]
                                - (PyPi)[https://www.pypi.org/project]
                            
                            Install:
                                ```pip install ip-reveal-headless```
 """

CLIENTS = []
"""
(list) - A list containing all the client objects for easy access to all.
"""

NICKS = []
"""
(list) - A list of the nicknames of clients connected to the server.
"""

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
"""
(socket) - The 'SERVER' socket object. Set up with 'socket.AF_INET' and 
'socket.SOCK_STREAM'
"""

PORT = 5300
"""
(int) - The port number we'd like to listen on.
"""

server_addr = f'{HOST}:{PORT}'
"""
(str) - The full server address in the format of 'HOST:PORT'.
"""

CLIENT_MANIFEST = {}
"""
(dict) - Contains all the information for each connected client.
"""


def server_startup():
    """
    Start the server.

    Goes through server socket prep;
        1) Binds to the provided host, and port.
        2) Begins listening.

    Returns:
        None
    """
    SERVER.bind((HOST, PORT))
    SERVER.listen()


def broadcast(message):
    """
    Broadcast a message to everyone on the client-list.
    Args:
        message:
            The message to send to clients

    Returns:
        None
    """
    for client in CLIENTS:
        client.send(message)


def handle(client):
    """
    Handle an ongoing connection with the client.

    Contains the main loop for sending and receiving messages to and from the
    client

    Arguments:
        client:
            The client object from the socket connection.

    Returns:
        None
    """
    nick = NICKS[-1]
    while True:
        try:
            message = client.recv(1024)
            print(f'MSG {message}')
            broadcast(f'<<{nick}>> {message}'.encode('ascii'))
        except Exception:
            index = CLIENTS.index(client)
            CLIENTS.remove(client)
            client.close()
            nick = NICKS[index]
            print(f'DISCONNECT {nick}')
            broadcast(f"{nick} left the server!".encode('ascii'))
            NICKS.remove(nick)
            break


def new_uuid():
    """
    Generate a UUID for a connecting client.

    For 'just-in-case' reasons, we start a loop before generating a UUID and then check the generated UUID against the
    client manifest. If the uid is novel we'll break out of the loop and return it to the caller. Otherwise, we let the
    loop run again. This process will repeat until a unique UUID has been generated. At this point we break outta the
    loop and return our generation to the caller.

    Note:
        I do not expect that this fail-safe will ever come into play, but better safe than HALTed/exploited.

    Returns:
        A UUID (String):
            A unique identifier for a connecting client.

    """
    uid = None

    while True:
        uid = uuid4()
        if uid not in CLIENT_MANIFEST.keys():
            break

    return uid


def client_send(client, msg):
    """
    Send a message to the provided client socket connection.

    Arguments:
        client:
            The client object from the socket connection.

        msg:
            The message that we want to send to the socket connection.

    Returns:
        None
    """
    client.send(msg.encode('ascii'))


def client_receive(client):
    """
    Receive incoming message from client.

    Receive 1024 bits and decode it before returning it to caller.

    Arguments:
        client:
            The client object from the incoming socket connection from client.

    Returns:
        String:
            The decoded message from the client.
    """
    return client.recv(1024).decode('ascii')


def req_from_client(client, pointer):
    """
    The req_from_client function sends a REQ request to the client.

    The 'pointer' parameter must be one of; UUID, NICK. Not case sensitive.


    Args:
        client: Send messages to the client
        pointer: Determine what data is sent to the client

    Returns:
        The value of the pointer parameter
    """
    pointers = [
        'UUID',
        'NICK'
    ]

    # Convert whatever string is in the 'pointer' parameter to uppercase.
    pointer = pointer.upper()

    # If an invalid pointer string was sent we raise a ValueError and send a
    # message informing of this
    if pointer.upper() not in pointers:
        raise ValueError(f"The 'pointer' parameter must be one of; {', '.join(pointers)}. Not '{pointer}'.")

    client_send(client, f'REQ {pointer}')

    return client_receive(client)


def handshake(client):
    print('HANDSHAKE START')

    # Get wanted nickname
    client_send(client, 'REQ NICK')
    nickname = client_receive(client)

    client_uuid = uuid4()
    connection_uuid = uuid4()

    print(f'CLIENT UUID CREATE {client_uuid}')
    print(f'CONNECTION UUID CREATE {connection_uuid}')

    client_send(client, 'REQ UUID')
    provided_uuid = client_receive(client)


def receive():
    """
    The 'receive' function is a loop that runs until the client disconnects from the server.
    It receives messages from the client and broadcasts them to all other clients.
    """
    while True:
        client, addr = SERVER.accept()

        print(f'CONNECT {addr}')

        client_send(client, 'REQ NICK')

        nick = client.recv(1024).decode('ascii')

        client_uuid = uuid4()
        connection_uuid = uuid4()

        print(f'CLIENT UUID CREATE {client_uuid}')
        print(f'CONNECTION UUID CREATE {connection_uuid}')

        client.send('REQ UUID'.encode('ascii'))

        CLIENT_MANIFEST[client_uuid] = {

        }

        NICKS.append(nick)
        CLIENTS.append(client)

        print(f'{addr} IDENTLOW {nick}')
        broadcast(f'{nick}@{addr} joined!'.encode('ascii'))
        client.send('You have been connected to the server'.encode('ascii'))

        thread = Thread(target=handle, args=(client,))
        thread.start()


if __name__ == '__main__':
    server_startup()
    receive()
