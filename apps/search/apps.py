
class SearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.search'

    def ready(self):
        from django.conf import settings
        if not hasattr(settings, 'SEARCH_USE_OLLAMA'):
            settings.SEARCH_USE_OLLAMA = True
        if not hasattr(settings, 'SEARCH_OLLAMA_TIMEOUT'):
            settings.SEARCH_OLLAMA_TIMEOUT = 30