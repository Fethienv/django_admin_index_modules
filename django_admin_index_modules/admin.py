from django.apps import apps
from django.contrib.admin.sites import AdminSite, AlreadyRegistered, NotRegistered
from django.views.decorators.cache import never_cache

from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.base import View

from django.utils.translation import gettext_lazy as _
"""
<link href='https://unpkg.com/boxicons@2.1.1/css/boxicons.min.css' rel='stylesheet'>
"""
class CustomAdminSite(AdminSite):

    index_template = "admin/dashboard.html"

    _modules_registry = {
        "top":{},
        "middle_top":{},
        "middle_bottom":{},
        "bottom":{}
    }
    _extra_js = []
    _extra_css = []

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps with icon that have been
        registered in this site.
        we added icon here
        """
        app_dict = self._build_app_dict(request)

        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])
            app['icon'] = apps.get_app_config(app["app_label"]).icon if hasattr(apps.get_app_config(app["app_label"]),"icon") else None 
            
        return app_list

    # def each_context(self, request):
    #     """
    #     Return a dictionary of variables to put in the template context for
    #     *every* page in the admin site.

    #     We added app_full_list for sidebar apps
    #     """
    #     extra_context = super().each_context(request)
    #     #extra_context.update({})
    #     return extra_context

    #@never_cache
    def index(self, request, extra_context={}):
        """
        Display the main admin index page, which lists all of the installed
        apps that have been registered in this site.

        we added modules_modules to context
        """
        extra_context.update({
            'modules_dict': self._build_modules_dict(request),
            'show_app_list':False,
            'grp_dashboard':False,
            'extra_js':self._extra_js,
            'extra_css':self._extra_css,
        })
        return super().index(request, extra_context)

    def register_module(self, module_class_or_iterable, **kwargs):
        """
        Register the given module_class(s) with the given admin class.

        The module_class(s) should be module classes, not instances.

        If a module_class is already registered, raise AlreadyRegistered.

        If a module_class is abstract, raise ImproperlyConfigured.
        """
        position = kwargs["position"] if "position" in kwargs else "middle_top"

        if position not in self._modules_registry:
            raise ValueError("%s position not exist" % position)
        
        if not isinstance(position,str):
            raise ValueError("position value expect string")

        if not isinstance(module_class_or_iterable, tuple) and module_class_or_iterable.__bases__[0].__name__ == "AdminModuleView":
            module_class_or_iterable = [module_class_or_iterable]

        for module_class in module_class_or_iterable:
            module_name = module_class.__name__
            if not self.is_registered_module(module_name, position=position):
                self._modules_registry[position][module_name] = module_class
            else:
                msg = 'The module_class %s is already registered ' % module_name
                raise AlreadyRegistered(msg)


    def is_registered_module(self, module_name, **kwargs):
        """
        Check if a module class is registered with this `AdminSite`.
        """
        return module_name in self._modules_registry[kwargs["position"]]

    def unregister_module(self, module_class_or_iterable):
        """
        register the given module(s).

        If a model isn't already registered, raise NotRegistered.
        """

        if not module_class_or_iterable:
            raise NotRegistered('The module_class %s is not registered' % "module_name")

        if not isinstance(module_class_or_iterable, tuple) and module_class_or_iterable.__bases__[0].__name__ == "AdminModuleView":
            module_class_or_iterable = [module_class_or_iterable]

        for module_class in module_class_or_iterable:
            module_name = module_class.__name__
            if module_name not in self._modules_registry:
                raise NotRegistered('The module_class %s is not registered' % module_name)
            del self._modules_registry[module_name]

    def _build_modules_dict(self, request):

        modules_dict = {}
        module_uri = str(request.GET['module_uri']).lower() if 'module_uri' in request.GET else None

        for position, modules in self._modules_registry.items():
            if modules:
                for module_name, module_class in modules.items():

                    response = module_class.as_view()(request, module_uri=module_name)

                    module_content = _('Method Not Allowed (%s): %s') % (request.method, request.path) if response.status_code == 405 and module_uri == module_name.lower() and not response.content else (response.content).decode(response.charset)
                    
                    if position not in modules:
                        modules_dict[position] = []
                    
                    modules_dict[position].append(module_content)

        return modules_dict


class AdminModuleView(View):

    template_name = "default.html"
    permissions=['is_superuser']
    css = []
    js = []
    json_method_names = []

    def get(self, request, **kwargs):
        return {}

    def _check_permissions(self, request):
        for permission in self.permissions:
            if not hasattr(request.user,str(permission)) or not getattr(request.user,str(permission)):
                return False
        return True

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.

        if not self._check_permissions(request):
            return HttpResponse("")

        if not hasattr(self, "template_name") or self.template_name is None:
            raise ImproperlyConfigured("AdminModuleView requires a definition of 'template_name'")

        self.request = request
        module_uri = str(request.GET['module_uri']).lower() if 'module_uri' in request.GET else None
        is_allowed_method = request.method.lower() in self.http_method_names and hasattr(self, request.method.lower())
        is_json_method = request.method.lower() in self.json_method_names

        if is_allowed_method and module_uri == kwargs['module_uri']:
            handler = getattr(self, request.method.lower())
        elif (is_allowed_method and module_uri != kwargs['module_uri']) or \
             (not is_allowed_method and module_uri != kwargs['module_uri']):
            handler = getattr(self, 'get')
        else:
            if is_json_method:
                return JsonResponse({
                        'status':'false',
                        'message':'Method Not Allowed (%s): %s'% (request.method, request.path)
                    }, 
                    status=405
                )

            return self.http_method_not_allowed(request)   

        context = handler(request, *args, **kwargs)

        if not isinstance(context, dict):
            raise TypeError("%s method must return a dict" % handler)

        if self.css or self.js:
            from django.contrib.admin.sites import site
            site._extra_js.extend(self.js)
            site._extra_css.extend(self.css)

        context['module_uri'] = "?module_uri=%s" % kwargs['module_uri'].lower()
        context['module_name'] = kwargs['module_uri']

        if is_json_method:
            return JsonResponse(context)
        return render(request, 'admin/modules/' + self.template_name, context)



def register_module(position, site=None):
    """
    Register the given module(s) classes and wrapped AdminModuleView class with
    admin site:

    @register_module(position="middle_top")
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

    The `site` kwarg is an admin site to use instead of the default admin site.
    """

    from django.contrib.admin.sites import AdminSite, site as default_site

    def _admin_module_view_decorator(*admin_module_view_classes):

        module_position = position if isinstance(position, str) else "middle_top"

        def _admin_module_view_wrapper(module_position, module_site):

            admin_site = module_site or default_site

            if not isinstance(admin_site, AdminSite):
                raise ValueError('site must subclass AdminSite')

            for admin_module_view_class in admin_module_view_classes:
                if not issubclass(admin_module_view_class, AdminModuleView):
                    raise ValueError('Wrapped class must subclass AdminModuleView.')

            admin_site.register_module(admin_module_view_classes, position=module_position)

        return _admin_module_view_wrapper(module_position, site)
      
    return _admin_module_view_decorator if isinstance(position, str) else _admin_module_view_decorator(position)

