from inspy_logger import InspyLogger

from inspyred_chat.server.info import PROG

isl = InspyLogger(PROG, 'info')
LOG_DEVICE = isl.device
ROOT_LOGGER = LOG_DEVICE.start()
LOCAL_LOGGER = LOG_DEVICE.add_child(f'{PROG}.logger')

ll = LOCAL_LOGGER
ll.debug('Logger started')
