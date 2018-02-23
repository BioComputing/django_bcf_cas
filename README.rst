=====
BCF CAS
=====

bcf-cas is a package to enable CAS authentication.

Quick start
-----------

1. Add 'bcf-cas' to your INSTALLED_APPS setting::

    INSTALLED_APPS = (
        ...
        'bcf_cas',
    )

2. Include the bcf-cas URLconf in your project urls.py::

    url(r'', include('bcf_cas.urls')),

    or

    url(r'^someurl/login$', 'bcf_cas.views.login'),
    url(r'^someurl/logout$', 'bcf_cas.views.logout')

3. Include the authentication backend in your settings.py::

    AUTHENTICATION_BACKENDS = (
        ...
        'bcf_cas.backends.CASBackend',
        ...
    )

4. Include the CAS middleware::

    MIDDLEWARE_CLASSES = (
        ...
        'bcf_cas.middleware.CASMiddleware',
        ...
    )

5. Include the CAS settings in settings.py::

    CAS_SERVER_URL = 'https://webauth.arizona.edu/webauth/validate'
    CAS_LOGOUT_COMPLETELY = True
    CAS_PROVIDE_URL_TO_LOGOUT = True
    
    CAS_NO_REDIRECT = False # enable this if using a custom django admin login page
