import shutil
from configparser import ConfigParser
from os import makedirs
from pathlib import Path
from sys import argv
from time import localtime
from inspyred_chat.server.info import DEFAULT_CONFIG_DIR, CONFIG_FILE_NAME, CONFIG_FILE_EXTENSION
from inspyred_chat.server.config.errors import InsaneBackupRateDetectionError

FILE_DIRPATH = Path(__file__).parent
CACHE_BACKUPS_DIRPATH = FILE_DIRPATH.joinpath('backups')


def backup_exists(backup_name):
    bp = CACHE_BACKUPS_DIRPATH.joinpath(backup_name).expanduser().resolve()

    return bp.exists()


def generate_backup_name():
    lt = localtime()
    day = str(lt[2]).zfill(2)
    month = str(lt[1]).zfill(2)
    year = str(lt[0])

    ext = 'bkup'

    backup_name = f'{month}_{day}_{year}'

    if backup_exists(str(f'{backup_name}.{ext}')):
        hour = str(lt[3]).zfill(2)
        minute = str(lt[4]).zfill(2)
        second = str(lt[5]).zfill(3)

        backup_name = backup_name + str(f'_{hour}_{minute}_{second}')

        if not backup_exists(backup_name):
            return str(backup_name + str(f'.{ext}'))
        else:
            raise InsaneBackupRateDetectionError()
    else:
        return str(backup_name + str(f'.{ext}'))


class Config:
    # ----------------------------------

    class Cache:
        FILE_DIRPATH = Path(__file__).parent
        filepath = FILE_DIRPATH.joinpath('.config.location').resolve()
        backup_dirpath = FILE_DIRPATH.joinpath('backups')

        def __init__(self, config_filepath=None, skip_load=False, skip_create=False):
            self.config_filepath = config_filepath
            self._loaded = False
            self.config_filepath = None

            if not self.exists and not skip_create:
                self.create()

            self.loadable = bool(self.exists)

            if self.loadable and not skip_load:
                self.config_filepath = self.load()

        @property
        def needs_loading(self):
            """
            The 'needs_loading' property returns a boolean based on if the config-cachefile still needs to be loaded.

            Calling this property will check that the cachefile exists and that it hasn't already been loaded to
            determine what to return.

            Returns:
                Boolean:
                   True: Yes, the cache file needs to be loaded. You can do this by calling on cache_obj.load().
                   False: No, the cache file need not be loaded as that's already been done, or it needs to be created.

                Note:
                    When you receive a 'bool(False)' response, it could mean one of two things;
                        - File doesn't exist:
                            If you've run the server before, this should not be the reason. You can rule this out by
                            checking one (or both) or two useful properties;
                                1.) calling the 'exists' property of your instantiated cache object, like so;
                                ```python
                                cache_obj.exists
                                --> True
                                ```

                                2.) calling the 'needs_saved' property of your instantiated cache object, like so;
                                ```python
                                cache_obj.needs_saved
                                --> False
                                ```
                                See the documentation for 'needs_saved' and 'exists' for more information.

                        - The contents of the cache file have already been loaded to memory. You can check this by
                        calling on the 'contents' property of the instantiated cache object in question, like so;
                        ```python
                        cache_obj.contents
                        --> C:\\Users\\taylor\\...
                        ```
            """
            return bool(self.exists and not self._loaded)

        @property
        def exists(self):
            """
            The exists property returns True if the file exists, and False otherwise.

            Note:
                If this returns with a 'False' boolean then it means that the cache-file does not exist or; at least
                that's what's reported by Path when calling Path('<path>').exists(). If you've successfully run the
                server on this machine, as the same user, within this filesystem, and in the same environment before,
                this can only happen (as far as I can foresee) if;
                    * User account lacks permissions to read the cache file
                        * Was the server first ran with elevated permissions?
                        * Was the server ran at any time with elevated permissions where the
                        configuration file location was also changed?
                        * Is either of the above true, but instead of elevated permissions it was
                        another user account?
                        * Has user-account directory access been changed?
                    or;
                    * The cache-file was deleted/renamed/moved since first-run.

            Returns:
                A boolean value
            """
            return self.filepath.exists()

        def load(self, traceback=True, ):
            """
            The 'load' method opens the file at self.filepath and loads its contents into the self.config_filepath
            instance-attribute.

            Returns:
                The method has two possible returns depending on if the file can be read or not;

                self.config_filepath:
                    A pathlib.Path object representing the location of the program's config file. (Returned after
                    successfully reading the file)

                None:
                    NoneType. (Returned after unsuccessfully attempting to read the file.

            """
            try:
                with open(self.filepath) as f:
                    self.config_filepath = Path(f.read()).resolve()
            except FileNotFoundError:
                print(f'No cachefile found at {self.filepath}!')
                return None
            except PermissionError:
                print(f'The cachefile at {self.filepath} is unable to be read due to insufficient privileges.')
                return None

            return self.config_filepath

        def create(self, exist_ok=False, backup_existing=True):

            # If self.config_filepath has still not been filled, we'll
            # fill it with 'DEFAULT_CONFIG_DIR'
            if self.config_filepath is None:
                self.config_filepath = DEFAULT_CONFIG_DIR.joinpath(f'{CONFIG_FILE_NAME}.{CONFIG_FILE_EXTENSION}')
            if self.exists and exist_ok:

                if backup_existing:
                    self.backup()
            elif not exist_ok and self.exists:
                raise FileExistsError()
            else:
                with open(self.filepath, 'wb') as file:
                    file.write(bytes(self.config_filepath))

            return self.filepath

        def backup(self):
            name = generate_backup_name()

            if not CACHE_BACKUPS_DIRPATH.exists():
                makedirs(CACHE_BACKUPS_DIRPATH)

            backup_filepath = f'{CACHE_BACKUPS_DIRPATH}/{str(name)}'

            if FILE_DIRPATH.joinpath('backups').exists():
                shutil.move(self.filepath, backup_filepath)

    # --------------------------------------------------

    def check_sections(self, skip_write=False):
        """
        The check_sections function checks to see if the USER section exists in the config file. If it does not exist,
        it is created and added to the config file.

        Arguments:
            self:
                Access the attributes and methods of the class in python

            skip_write:
                Indicate that the function should not write to the config file. (Defaults to bool(False))

        Returns:
            True
        """
        if 'USER' not in self.parser.sections():
            self.parser.add_section('USER')
            if not skip_write:
                self.save()

    def save(self):
        """
        The save function saves the current state of the config to a file.

        Args:
            self: Refer to the object itself

        Returns:
            The filepath that the config was saved to
        """
        with open(self.filepath, 'w') as file:
            self.parser.write(file)

        return self.filepath

    def load(self):
        """
        The load function loads the config information from a file into memory.

        Args:
            self: Reference the class itself

        Returns:
            A dictionary of the form {'x': x, 'y': y}
        """
        self.parser.read(self.filepath)

        return self.parser

    def create(self):
        """
        The create function creates a new instance of the class.
        It takes no arguments and returns an instance of the class.

        Args:
            self: Reference the object itself

        Returns:
            A tuple containing the new object and a boolean value of true
        """
        self.parser.read('example_config.ini')

    def __init__(self, config_dirpath=None):

        base_path = Path(__file__).parent
        path = None
        cache = self.Cache()

        self.parser = ConfigParser()

        if config_dirpath is None and '--config-file' in argv:
            self.filepath = Path(argv[argv.index('--config-file') + 1]).expanduser().resolve()

        self.filepath = cache.config_filepath
        print(self.filepath)

        self.dirpath = self.filepath.parent

        if not self.filepath.exists():
            if not self.dirpath.exists():
                makedirs(self.dirpath)
            example_conf = Path(Path(__file__).parent).joinpath('example_config.ini')
            shutil.copy(example_conf, self.filepath)

        if self.filepath is None:
            self.create()

        self.load()

        self.check_sections()
