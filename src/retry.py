"""Exponential backoff retry utility with jitter and structured logging.

This module provides a reusable retry mechanism with exponential backoff,
optional jitter, and hooks for structured logging integration.
"""

import random
import time
from typing import Any, Callable, Optional, Type, Union

from .logging_setup import LogEvents, get_logger

logger = get_logger("retry")


class RetryError(Exception):
    """Raised when retry attempts are exhausted or non-retryable exception encountered."""
    
    def __init__(self, message: str, last_exception: Optional[Exception] = None):
        super().__init__(message)
        self.last_exception = last_exception


def exponential_backoff_with_jitter(
    func: Callable[..., Any],
    *args,
    max_attempts: int = 5,
    base_delay: float = 0.5,
    max_delay: float = 30.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,),
    non_retryable_exceptions: tuple = (),
    before_attempt_hook: Optional[Callable[[int, float], None]] = None,
    on_error_hook: Optional[Callable[[int, Exception, float], None]] = None,
    **kwargs
) -> Any:
    """Execute function with exponential backoff retry and optional jitter.
    
    Args:
        func: Function to execute with retry logic
        max_attempts: Maximum number of retry attempts (must be > 0)
        base_delay: Base delay in seconds for exponential backoff (must be > 0)
        max_delay: Maximum delay cap in seconds (must be >= base_delay)
        jitter: Whether to apply full jitter to delay calculation
        retryable_exceptions: Tuple of exception types that should trigger retry
        non_retryable_exceptions: Tuple of exception types that should not trigger retry
        before_attempt_hook: Optional hook called before each attempt with (attempt, delay)
        on_error_hook: Optional hook called after each failed attempt with (attempt, exception, next_delay)
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func
        
    Returns:
        Result of successful function execution
        
    Raises:
        RetryError: When retry attempts are exhausted or non-retryable exception encountered
        
    Note:
        Exponential backoff formula: 2^(attempt-1) * base_delay, capped at max_delay
        Full jitter: Uniformly random delay between 0 and calculated delay
    """
    if max_attempts <= 0:
        raise ValueError("max_attempts must be > 0")
    if base_delay <= 0:
        raise ValueError("base_delay must be > 0")
    if max_delay < base_delay:
        raise ValueError("max_delay must be >= base_delay")
    
    last_exception = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            # Calculate delay for this attempt (used in hooks even for first attempt)
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            if jitter:
                delay = random.uniform(0, delay)
            
            # Call before attempt hook
            if before_attempt_hook:
                before_attempt_hook(attempt, delay)
            
            # Execute the function
            return func(*args, **kwargs)
            
        except Exception as e:
            last_exception = e
            
            # Check if this is a non-retryable exception
            if non_retryable_exceptions and isinstance(e, non_retryable_exceptions):
                logger.error(
                    LogEvents.RETRY_FAILED,
                    attempt=attempt,
                    max_attempts=max_attempts,
                    exception_type=type(e).__name__,
                    exception_message=str(e),
                    reason="non_retryable_exception"
                )
                raise RetryError(
                    f"Non-retryable exception after {attempt} attempts: {str(e)}",
                    last_exception=e
                )
            
            # Check if this is a retryable exception
            if not isinstance(e, retryable_exceptions):
                logger.error(
                    LogEvents.RETRY_FAILED,
                    attempt=attempt,
                    max_attempts=max_attempts,
                    exception_type=type(e).__name__,
                    exception_message=str(e),
                    reason="unexpected_exception_type"
                )
                raise RetryError(
                    f"Unexpected exception type after {attempt} attempts: {str(e)}",
                    last_exception=e
                )
            
            # If this is the last attempt, don't sleep and raise immediately
            if attempt >= max_attempts:
                logger.error(
                    LogEvents.RETRY_FAILED,
                    attempt=attempt,
                    max_attempts=max_attempts,
                    exception_type=type(e).__name__,
                    exception_message=str(e),
                    reason="max_attempts_exceeded"
                )
                raise RetryError(
                    f"Max retry attempts ({max_attempts}) exceeded. Last error: {str(e)}",
                    last_exception=e
                )
            
            # Calculate delay for next attempt
            next_delay = min(max_delay, base_delay * (2 ** attempt))
            if jitter:
                next_delay = random.uniform(0, next_delay)
            
            # Call error hook
            if on_error_hook:
                on_error_hook(attempt, e, next_delay)
            
            # Sleep before next attempt
            logger.warning(
                LogEvents.RETRY_BACKOFF,
                attempt=attempt,
                max_attempts=max_attempts,
                exception_type=type(e).__name__,
                exception_message=str(e),
                backoff_delay=next_delay
            )
            time.sleep(next_delay)
    
    # This should never be reached, but included for completeness
    raise RetryError(
        f"Retry logic error: exceeded max attempts without proper exception handling",
        last_exception=last_exception
    )


class RetryableOperation:
    """Context manager and decorator for retryable operations with structured logging."""
    
    def __init__(
        self,
        operation_name: str,
        max_attempts: int = 5,
        base_delay: float = 0.5,
        max_delay: float = 30.0,
        jitter: bool = True,
        retryable_exceptions: tuple = (Exception,),
        non_retryable_exceptions: tuple = ()
    ):
        self.operation_name = operation_name
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions
        self.non_retryable_exceptions = non_retryable_exceptions
    
    def _before_attempt_hook(self, attempt: int, delay: float) -> None:
        """Log attempt information."""
        logger.info(
            LogEvents.RETRY_ATTEMPT,
            operation=self.operation_name,
            attempt=attempt,
            max_attempts=self.max_attempts
        )
    
    def _on_error_hook(self, attempt: int, exception: Exception, next_delay: float) -> None:
        """Log error information."""
        logger.warning(
            LogEvents.RETRY_BACKOFF,
            operation=self.operation_name,
            attempt=attempt,
            max_attempts=self.max_attempts,
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            backoff_delay=next_delay
        )
    
    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator interface."""
        def wrapper(*args, **kwargs):
            return exponential_backoff_with_jitter(
                func,
                max_attempts=self.max_attempts,
                base_delay=self.base_delay,
                max_delay=self.max_delay,
                jitter=self.jitter,
                retryable_exceptions=self.retryable_exceptions,
                non_retryable_exceptions=self.non_retryable_exceptions,
                before_attempt_hook=self._before_attempt_hook,
                on_error_hook=self._on_error_hook,
                *args,
                **kwargs
            )
        return wrapper
    
    def execute(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        return exponential_backoff_with_jitter(
            func,
            max_attempts=self.max_attempts,
            base_delay=self.base_delay,
            max_delay=self.max_delay,
            jitter=self.jitter,
            retryable_exceptions=self.retryable_exceptions,
            non_retryable_exceptions=self.non_retryable_exceptions,
            before_attempt_hook=self._before_attempt_hook,
            on_error_hook=self._on_error_hook,
            *args,
            **kwargs
        )