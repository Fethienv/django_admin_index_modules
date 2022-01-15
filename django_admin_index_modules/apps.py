from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig
from django.utils.translation import gettext_lazy as _

class CustomAdminConfig(AdminConfig):
    default_site = 'django_admin_index_modules.admin.CustomAdminSite'


class ModulesDashboardsConfig(AppConfig):
    default_auto_field = 'django_admin_index_modules.db.models.BigAutoField'
    name = 'django_admin_index_modules'
