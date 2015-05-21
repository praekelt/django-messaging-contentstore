django-messaging-contentstore
================================

A RESTful API for managing collections of messaging content. Comes with a
client and a fake.


::

    $ virtualenv ve
    $ source ve/bin/activate
    (ve)$ pip install -r requirements.txt
    (ve)$ pip install -r requirements-dev.txt
    (ve)$ py.test --ds=testsettings contentstore/tests.py --cov=contentstore


Configuration
-------------------------------

The following configuration (with dummy values replaced by real ones) needs to
be added to ``settings.py`` to configure this app::

    INSTALLED_APPS = [
        # Usual Django stuff plus
        # Third-party apps
        'djcelery',
        'rest_framework',
        'rest_framework.authtoken',
        'django_filters'
    ]

    # REST Framework conf defaults
    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
        'PAGINATE_BY': None,
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.BasicAuthentication',
            'rest_framework.authentication.TokenAuthentication',
        ),
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
        ),
        'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)
    }



Release Notes
------------------------------
0.1.3 - 2015-05-21 - Initial release
