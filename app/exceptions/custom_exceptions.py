from fastapi import status


class AppException(Exception):
    """Base exception for expected application errors."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class BadRequestException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST


class NotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND


class ConflictException(AppException):
    status_code = status.HTTP_409_CONFLICT


class PayloadTooLargeException(AppException):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


class UnprocessableEntityException(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
