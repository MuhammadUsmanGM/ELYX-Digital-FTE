import time
from collections import defaultdict, deque
from typing import Dict, Optional
import threading

class RateLimiter:
    def __init__(self):
        self.limits = {}  # Dictionary to store rate limits for different services
        self.request_times = defaultdict(deque)  # Track request times
        self.lock = threading.Lock()  # Thread safety

    def set_limit(self, service: str, max_requests: int, time_window: int):
        """
        Set rate limit for a service

        Args:
            service: Name of the service (e.g., 'gmail', 'linkedin', 'whatsapp')
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        with self.lock:
            self.limits[service] = {
                'max_requests': max_requests,
                'time_window': time_window
            }

    def is_allowed(self, service: str) -> bool:
        """
        Check if a request to the service is allowed based on rate limits

        Args:
            service: Name of the service

        Returns:
            True if request is allowed, False otherwise
        """
        with self.lock:
            if service not in self.limits:
                # If no limit is set, allow the request
                return True

            limit_config = self.limits[service]
            max_requests = limit_config['max_requests']
            time_window = limit_config['time_window']

            current_time = time.time()

            # Clean up old request times outside the time window
            while (self.request_times[service] and
                   current_time - self.request_times[service][0] > time_window):
                self.request_times[service].popleft()

            # Check if we're under the limit
            if len(self.request_times[service]) < max_requests:
                # Record this request time
                self.request_times[service].append(current_time)
                return True

            # Rate limit exceeded
            return False

    def wait_if_needed(self, service: str) -> float:
        """
        Wait if needed to respect rate limits.
        Calculates wait time under lock, then sleeps outside the lock (#65).

        Args:
            service: Name of the service

        Returns:
            Number of seconds waited, or 0 if no wait was needed
        """
        if self.is_allowed(service):
            return 0.0

        wait_time = 0.0
        with self.lock:
            if service not in self.limits or not self.request_times[service]:
                return 0.0

            limit_config = self.limits[service]
            time_window = limit_config['time_window']

            earliest_request = self.request_times[service][0]
            wait_time = time_window - (time.time() - earliest_request)

        # Sleep OUTSIDE the lock so other threads aren't blocked
        if wait_time > 0:
            time.sleep(wait_time)
            return wait_time

        return 0.0

    def get_remaining_quota(self, service: str) -> int:
        """
        Get the number of requests remaining in the current time window

        Args:
            service: Name of the service

        Returns:
            Number of requests remaining
        """
        with self.lock:
            if service not in self.limits:
                return float('inf')  # Unlimited if no limit set

            limit_config = self.limits[service]
            max_requests = limit_config['max_requests']

            # Clean up old request times
            current_time = time.time()
            while (self.request_times[service] and
                   current_time - self.request_times[service][0] > limit_config['time_window']):
                self.request_times[service].popleft()

            return max_requests - len(self.request_times[service])

    def get_reset_time(self, service: str) -> float:
        """
        Get the time when the rate limit will reset

        Args:
            service: Name of the service

        Returns:
            Unix timestamp when the rate limit will reset
        """
        with self.lock:
            if service not in self.limits or not self.request_times[service]:
                return time.time()

            limit_config = self.limits[service]
            time_window = limit_config['time_window']

            # The reset time is the time of the earliest request plus the time window
            earliest_request = self.request_times[service][0]
            return earliest_request + time_window


# Pre-configured rate limiters for common services
class ServiceRateLimiters:
    def __init__(self):
        self.gmail = RateLimiter()
        self.gmail.set_limit('gmail', max_requests=250, time_window=86400)  # 250/day

        self.linkedin = RateLimiter()
        self.linkedin.set_limit('linkedin', max_requests=100, time_window=3600)  # 100/hour

        self.whatsapp = RateLimiter()
        self.whatsapp.set_limit('whatsapp', max_requests=50, time_window=3600)  # 50/hour

        self.facebook = RateLimiter()
        self.facebook.set_limit('facebook', max_requests=50, time_window=3600)  # 50/hour

        self.twitter = RateLimiter()
        self.twitter.set_limit('twitter', max_requests=100, time_window=3600)  # 100/hour

        self.instagram = RateLimiter()
        self.instagram.set_limit('instagram', max_requests=25, time_window=3600)  # 25/hour

    def get_limiter(self, service: str) -> RateLimiter:
        """Get the appropriate rate limiter for a service"""
        svc = service.lower()
        for name in ('gmail', 'linkedin', 'whatsapp', 'facebook', 'twitter', 'instagram'):
            if svc == name:
                return getattr(self, name)
        # Default conservative limits
        default = RateLimiter()
        default.set_limit(service, max_requests=10, time_window=60)
        return default


# Global instance for easy access
rate_limiters = ServiceRateLimiters()


def check_rate_limit(service: str) -> bool:
    """
    Convenience function to check if a request to a service is allowed

    Args:
        service: Name of the service (e.g., 'gmail', 'linkedin', 'whatsapp')

    Returns:
        True if request is allowed, False otherwise
    """
    limiter = rate_limiters.get_limiter(service)
    return limiter.is_allowed(service)


def wait_for_rate_limit(service: str) -> float:
    """
    Convenience function to wait if needed to respect rate limits

    Args:
        service: Name of the service (e.g., 'gmail', 'linkedin', 'whatsapp')

    Returns:
        Number of seconds waited
    """
    limiter = rate_limiters.get_limiter(service)
    return limiter.wait_if_needed(service)