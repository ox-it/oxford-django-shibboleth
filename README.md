# oxford-django-shibboleth

A Django authentication backend that uses attributes released through Shibboleth to populate user attributes and groups. It uses the following claims:

* eduPersonPrincipalName → username
* givenName → first_name
* sn → last_name
* mail → email
* oakStatus → `status:{status}` group membership
* oakITSSFor → `itss` and `itss:{unit}` group membership
* eduPersonOrgUnitDN → `affiliation:{unit}` group membership


## Usage

Add it to your `AUTHENTICATION_BACKENDS` in your Django settings module:

```python
AUTHENTICATION_BACKENDS = (
    'djoxshib.backends.ShibbolethBackend',
)
```

Add ``LoginView`` to your urls:

```python
from django.contrib.auth.views import LoginView
from django.urls import path

urlpatterns = (
    ...
    path('login/', LoginView.as_view(), name='login'),
    ...
)
```

Configure `mod_shib` to protect the login view:

```apache
<Location "/login/">
    Require valid-user
    AuthType shibboleth
    ShibRequestSetting requiresession On
</Location>
```

