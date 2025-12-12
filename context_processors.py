"""
Custom context processors for the store app.
This makes variables available to all templates.
"""

from django.conf import settings


def language_processor(request):
    """
    Add language settings to the template context.
    This makes LANGUAGES available in all templates.
    """
    return {
        'LANGUAGES': settings.LANGUAGES,
        'current_language': request.LANGUAGE_CODE if hasattr(request, 'LANGUAGE_CODE') else settings.LANGUAGE_CODE,
    }
