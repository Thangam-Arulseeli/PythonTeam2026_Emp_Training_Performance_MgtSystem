
class AppException(Exception):
    def __init__(self, message: str):

        """Base exception for handling custom application errors."""

        self.message = message
        super().__init__(message)


class EmployeeNotFoundException(AppException):
    def __init__(self):
    
        """Indicate that an employee was not found or is inactive."""
    
        super().__init__("Employee not found or not active")


class EmployeeAlreadyExistsException(AppException):
    def __init__(self, field: str):

        """Indicate that an employee with the specified field already exists."""
        super().__init__(
            f"Employee with this {field} already exists"
        )


class EmployeeInactiveException(AppException):
    def __init__(self):
        """Indicate that the employee account is inactive."""

        super().__init__("Employee is inactive")


class InvalidEmployeeDataException(AppException):
    def __init__(self, message: str):
        """Indicate that employee data is invalid."""
        super().__init__(message)
