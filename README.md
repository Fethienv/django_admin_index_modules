Django admin index modules
=======================

Django admin index modules is a Django app that gives you the ability to add widgets modules to the django admin dashboard (admin index).


Quick start
-----------
1. Installation:

```
pip install django-admin-index-modules
```

2. comment "django.contrib.admin" and add "django_admin_index_modules.apps.CustomAdminConfig" to your INSTALLED_APPS setting like this:

```
    INSTALLED_APPS = [
        ...
        #'django.contrib.admin',
        'django_admin_index_modules.apps.CustomAdminConfig',
        ...

        'django.contrib.staticfiles',
        ...

        'django_admin_index_modules.apps.ModulesDashboardsConfig',
        ...
    ]
```
3. In admin.py file of any other app create ypur widget module like this:

```
    from django_admin_index_modules.admin import AdminModuleView

    class VisitorsAdminModuleView(AdminModuleView):

        template_name = 'visitors.html'
        json_method_names = ['post']
        http_method_names = ['get','post']
        permissions = ['is_superuser']
        css = []
        js = []

        def get(self, request, **kwargs):
            context = {
                'stats': "visitors"
            }
            return context
```

4. register your widget module using one of those methods:

4. 1. using register_module(AdminModuleView, position="middle_top") methods:

```
    from django.contrib import admin

    admin.site.register_module(VisitorsAdminModuleView, position="middle_top")
```

4. 2. using @register_module(position="middle_top") decorator:

```
    from django_admin_index_modules.admin import register_module

    @register_module(position="middle_top")
    class VisitorsAdminModuleView(AdminModuleView):
        ...
```

4. 3. position keyword can take one of those values: top, middle_top, middle_bottom and bottom

5. create template file under "admin/modules/" than the name of the template file assigned to template_name propriety ex: "visitors.html"

6. Visit http://127.0.0.1:8000/admin/ to see your widget module.