from argparse import ArgumentParser
from inspyred_chat.server.info import DEFAULT_CONFIG_DIR, PROG, LOG_LEVELS, DEFAULT_PORT


class CLIArgs(ArgumentParser):
    def __init__(self, config):
        """
        Sets up command-line arguments for the program.
        """
        super().__init__()
        self._parsed = None

        self.description = 'A simple chat server.'
        self.prog = PROG

        c_file_divergent = False

        if DEFAULT_CONFIG_DIR != config.filepath:
            config_help_default_statement = 'Setting this will override currently set config ' \
                                            f'filepath: {config.filepath}'
            config_arg_default = config.filepath
            c_file_divergent = True
        else:
            config_help_default_statement = 'The default config filepath is: ' \
                                            f'{DEFAULT_CONFIG_DIR.joinpath("config.ini")}'
            config_arg_default = DEFAULT_CONFIG_DIR

        if DEFAULT_PORT != config.parser.get('USER', 'port'):
            port_arg_default = config.parser.get('USER', 'port')
            port_help_statement = f'Setting this will override your currently set port which is {port_arg_default}'
        else:
            port_arg_default = DEFAULT_PORT
            port_help_statement = f'The default is: {port_arg_default}'

        self.add_argument(
            '-c',
            '--config-file',
            action='store',
            help='The location of where an existing config file is, or where you want a new one placed. '
                 f'{config_help_default_statement}',
            required=False,
            default=config_arg_default

        )

        self.add_argument(
            '-p',
            '--port',
            action='store',
            required=False,
            help=f'The port which you\'d like the server to bind to. {port_help_statement}',
            default=port_arg_default,
        )

        if c_file_divergent:
            self.add_argument(
                '--reset-config-file',
                action='store_true',
                help=f'Create a new config file at the default developer\'s recommended location: {DEFAULT_CONFIG_DIR}',
                required=False,
                default=False,
            )

        self.add_argument(
            '-b',
            '--bind-address',
            '--bind-addr',
            action='store',
            required=False,
            help='The address the server should bind to.',
            default='127.0.0.1'

        )

        self.add_argument(
            '-l',
            '--log-level',
            action='store',
            help='The level at which the logger should output messages.',
            default='info',
            required=False,
            choices=LOG_LEVELS

        )

    @property
    def parsed(self):
        """

        The parsed arguments as a dictionary.

        On first request of this property's value after instantiation of this it's parent class (CLIArgs) the arguments
        have not yet been parsed. When one first asks for the value of this property it is then evaluated.
        ArgParser().parse_args is run, the returned dictionary is set as the property value, and then the property value
        is returned.

        Note:
            Subsequent references to this property performed on this particular instance of CLIArgs will *never* return
            a resulting dictionary that differs from those received on previous references.

        Returns:
            argparse.ArgumentParser().parse_args:
                The command-line arguments, parsed into dictionary form.

        """
        if not self._parsed:
            self._parsed = self.parse_args()

        return self._parsed
