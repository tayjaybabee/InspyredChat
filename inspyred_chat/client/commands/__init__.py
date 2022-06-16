

def handle_command(cmd):
    pass


def disconnect_from_server(server_instance, quit_msg='Leaving.'):
    server_instance.close()

valid_commands = {
    'disconnect': {
        'func': disconnect_from_server
    }
}

CMD_PREFIX = '/'
