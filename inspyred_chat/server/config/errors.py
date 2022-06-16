class InsaneBackupRateDetectionError(Exception):
    message = 'More than 1 backup a second is not needed!'

    def __init__(self, message=message):
        """
        Raised when 'inspyred_chat.server.config' finds that a backup from this second already exists.
        Args:
            message (String):
                 Any additional information that needs to be conveyed.
        """
        if message != self.message:
            self.message = f'\nSome additional information from the caller: {message}'

        super(InsaneBackupRateDetectionError, self).__init__(self.message)
