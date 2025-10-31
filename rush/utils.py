"""
Utility functions for the RUSH application.
"""


def get_client_ip(group, request):
    """
    Get the real client IP address from the request, accounting for reverse proxies.

    Checks X-Forwarded-For and X-Real-IP headers that are set by Nginx proxy.
    Falls back to REMOTE_ADDR if no proxy headers are present.

    Args:
        request: Django HttpRequest object

    Returns:
        str: Client IP address
    """
    # Check X-Forwarded-For header (set by Nginx)
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # X-Forwarded-For can contain multiple IPs (client, proxy1, proxy2, ...)
        # The first one is the original client IP
        ip = x_forwarded_for.split(",")[0].strip()
        return ip

    # Check X-Real-IP header (also set by Nginx)
    x_real_ip = request.META.get("HTTP_X_REAL_IP")
    if x_real_ip:
        return x_real_ip.strip()

    # Fall back to REMOTE_ADDR (direct connection, no proxy)
    return request.META.get("REMOTE_ADDR", "")
