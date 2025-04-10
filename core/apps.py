from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    # def ready(self):
    #     import core.signals
    #     import core.roles  # Ensure roles are loaded
    #     import core.permissions  # Ensure permissions are loaded
    