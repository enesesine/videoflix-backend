"""
Expose the front-end base URL to all Django templates.

Usage in template:
    {{ frontend_url }}
"""

from django.conf import settings


def frontend_url(_request):
    """Return a context dict containing the public front-end URL."""
    return {"frontend_url": settings.FRONTEND_URL}
