from exceptions.error_codes import ErrorCodes


class ServiceException(Exception):
    def __init__(self, status_code: int, error_code: ErrorCodes, message: str, rest_obj: dict = None) -> None:
        """
        Custom exception class for representing service-level exceptions.

        :param status_code: HTTP status code.
        :param error_code: Enum value representing the error code.
        :param message: Error message.
        :param rest_obj: Additional data related to the error (optional).
        """
        super().__init__(message)
        self.status_code = status_code
        self.rest_obj = rest_obj
        self.error_code = error_code.value
        self.message = message
