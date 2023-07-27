from click import ClickException


class ProjectValidationError(ClickException):
    """
    Raised when project checks fail
    """

    pass


class InvalidConfiguration(ClickException):
    """
    Raised when invalid pyproject.toml file
    """
