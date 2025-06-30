from django.conf import settings

def frontend_url(_request):
    """Stellt {{ frontend_url }} in Templates bereit."""
    return {"frontend_url": settings.FRONTEND_URL}
