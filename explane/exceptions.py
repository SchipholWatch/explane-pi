class DeviceError(Exception):
    """Represents an error with an external device that cannot be recovered from."""


class ExternalServiceError(Exception):
    """Represents a failure at an external service that is outside of our influence."""
