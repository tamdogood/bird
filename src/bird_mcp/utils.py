"""Shared utilities for Bird MCP server."""

import asyncio
import logging
from functools import wraps
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


def handle_errors(service_name: str):
    """Decorator for consistent error handling across tools.

    Args:
        service_name: Name of the service (e.g., "Todoist", "Anki")

    Returns:
        Decorated function with error handling
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> dict[str, Any]:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"{service_name} error in {func.__name__}: {e}",
                    exc_info=True
                )
                return {
                    "success": False,
                    "error": f"{service_name} error: {str(e)}",
                    "error_type": type(e).__name__,
                }
        return wrapper
    return decorator


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for retrying failed operations with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (doubles with each retry)

    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for "
                            f"{func.__name__}: {e}. Retrying in {delay}s..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries} attempts failed for {func.__name__}"
                        )

            raise last_exception
        return wrapper
    return decorator


class BaseIntegration:
    """Base class for all service integrations."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def health_check(self) -> dict[str, Any]:
        """Check if the service is accessible and healthy.

        Returns:
            Health status dictionary
        """
        raise NotImplementedError("Subclasses must implement health_check")

    async def get_info(self) -> dict[str, Any]:
        """Get basic information about the integration.

        Returns:
            Integration information dictionary
        """
        raise NotImplementedError("Subclasses must implement get_info")
