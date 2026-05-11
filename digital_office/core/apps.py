from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "digital_office.core"
    verbose_name = "Core domain"
    def ready(self):
        # Ensure default user groups exist for access control
        try:
            from django.contrib.auth.models import Group
            Group.objects.get_or_create(name="client")
            Group.objects.get_or_create(name="manager")
        except Exception:
            pass
