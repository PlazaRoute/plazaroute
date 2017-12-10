class ValidationError(ValueError):
    """
    Exception for validation errors.
    The provided exception msg will be exposed to the user.
    """
    pass


class ServiceError(Exception):
    """
    Exception for service failures in the integration layer.
    """
    pass
