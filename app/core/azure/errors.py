class AzureError(Exception):
    """Base for Azure-related failures."""


class AzureConfigError(AzureError):
    """Server misconfiguration (missing key/region)."""


class AzureUnavailableError(AzureError):
    """Network/upstream failure talking to Azure."""


class AzureTokenError(AzureError):
    """Azure returned a non-200 for the token request."""
