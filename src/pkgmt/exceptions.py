from click import ClickException


class ProjectValidationError(ClickException):
    """
    Raised when project checks fail
    """

    pass
