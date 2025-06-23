from django.conf import settings


def base_media_url(request):
    base_url = request.build_absolute_uri("/")
    return {
        "BASE_MEDIA_URL": base_url.rstrip("/") + settings.MEDIA_URL,
    }
