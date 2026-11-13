
class AppException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class EmployeeNotFoundException(AppException):
    def __init__(self):
        super().__init__("Employee not found or not active")


class EmployeeAlreadyExistsException(AppException):
    def __init__(self, field: str):
        super().__init__(
            f"Employee with this {field} already exists"
        )


class EmployeeInactiveException(AppException):
    def __init__(self):
        super().__init__("Employee is inactive")


class InvalidEmployeeDataException(AppException):
    def __init__(self, message: str):
        super().__init__(message)
