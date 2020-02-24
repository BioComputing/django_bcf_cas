"""CAS authentication middleware"""

try:
    # python3
    from urllib.parse import urlencode
except ImportError:
    # python2
    from urllib import urlencode

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import logout as do_logout
from django.contrib.auth import login, logout
# from django.contrib.auth.views import LoginView, LogoutView

try:
    from django.core.urlresolvers import reverse
except ModuleNotFoundError:
    from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.exceptions import ImproperlyConfigured

from bcf_cas.exceptions import CasTicketException
from bcf_cas.views import login as cas_login, logout as cas_logout

__all__ = ['CASMiddleware']


class CASMiddleware(object):
    """Middleware that allows CAS authentication on admin pages"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        """Checks that the authentication middleware is installed"""

        error = ("The Django CAS middleware requires authentication "
                 "middleware to be installed. Edit your MIDDLEWARE_CLASSES "
                 "setting to insert 'django.contrib.auth.middleware."
                 "AuthenticationMiddleware'.")
        assert hasattr(request, 'user'), error

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Forwards unauthenticated requests to the admin page to the CAS
        login URL, as well as calls to django.contrib.auth.views.login and
        logout.
        """
        # optional setting for custom admin login pages
        if hasattr(settings, 'CAS_NO_REDIRECT') and settings.CAS_NO_REDIRECT:
            return None

        if view_func == login:
            print("LOGIN VIEW")
            return cas_login(request, *view_args, **view_kwargs)
        elif view_func == logout:
            return cas_logout(request, *view_args, **view_kwargs)

        if settings.CAS_ADMIN_PREFIX:
            if not request.path.startswith(settings.CAS_ADMIN_PREFIX):
                return None
        elif not view_func.__module__.startswith('django.contrib.admin.'):
            return None

        if request.user.is_authenticated:
            if request.user.is_staff:
                return None
            else:
                error = ('<h1>Forbidden</h1><p>You do not have staff '
                         'privileges.</p>')
                return HttpResponseForbidden(error)
        params = urlencode({REDIRECT_FIELD_NAME: request.get_full_path()})
        return HttpResponseRedirect(reverse(cas_login) + '?' + params)

    def process_exception(self, request, exception):
        """When we get a CasTicketException, that is probably caused by the ticket timing out.
        So logout/login and get the same page again."""
        if isinstance(exception, CasTicketException):
            do_logout(request)
            # This assumes that request.path requires authentication.
            return HttpResponseRedirect(request.path)
        else:
            return None


class ProxyMiddleware(object):

    # Middleware used to "fake" the django app that it lives at the Proxy Domain
    def process_request(self, request):
        proxy = getattr(settings, 'PROXY_DOMAIN', None)
        if not proxy:
            raise ImproperlyConfigured('To use Proxy Middleware you must set a PROXY_DOMAIN setting.')
        else:
            request.META['HTTP_HOST'] = proxy
