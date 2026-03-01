from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "content"
    verbose_name = "Content Management"

    def ready(self):
        """
        Called when Django starts.
        Defer DB-dependent social auth config to the first request to avoid
        the "Accessing the database during app initialization" RuntimeWarning.
        """
        from django.core.signals import request_started

        def _load_social_auth(**_kwargs):
            # Disconnect immediately — only needs to run once
            request_started.disconnect(_load_social_auth)
            from django.conf import settings
            try:
                from content.social_auth_config import get_socialaccount_providers
                providers = get_socialaccount_providers()
                if providers:
                    settings.SOCIALACCOUNT_PROVIDERS.update(providers)
            except Exception as e:
                import sys
                if "migrate" not in sys.argv and "makemigrations" not in sys.argv:
                    print(f"Warning: Could not load social auth config: {e}")

        request_started.connect(_load_social_auth)
