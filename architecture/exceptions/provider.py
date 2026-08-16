class ProviderError(Exception):
    """Base provider exception."""


class ProviderRateLimitError(ProviderError):
    """Provider rate limit exceeded."""


class ProviderConnectionError(ProviderError):
    """Temporary connection problem."""


class ProviderAuthenticationError(ProviderError):
    """Authentication failed."""
