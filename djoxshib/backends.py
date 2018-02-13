import re
from django.contrib.auth.backends import RemoteUserBackend

from django.contrib.auth.models import Group
from django.db.models import Q


class ShibbolethBackend(RemoteUserBackend):
    redirect_authenticated_user = True

    attribute_map = [
        ('givenName', 'first_name'),
        ('sn', 'last_name'),
        ('mail', 'email'),
    ]

    def authenticate(self, request, remote_user):
        user = super().authenticate(request, remote_user)
        if user:
            self.update_user_data(request, user)

        return user

    def update_user_data(self, request, user):
        for shib_attribute, user_attribute in self.attribute_map:
            if shib_attribute in request.META:
                setattr(user, user_attribute, request.META[shib_attribute])
            else:
                setattr(user, user_attribute, user._meta.fields_map[user_attribute].default)
        user.save()

        groups = set()

        if 'oakStatus' in request.META:
            groups.add('status:{}'.format(request.META['oakStatus']))

        for orgunit_dn in request.META.get('orgunit-dn', '').split(';'):
            match = re.match('^oakUnitCode=(.*),ou=units,dc=oak,dc=ox,dc=ac,dc=uk$', orgunit_dn)
            if match:
                groups.add('affilition:{}'.format(match.group(1)))

        for oak_itss_for in request.META.get('oakITSSFor', '').split(';'):
            match = re.match('^oakGN=ITSS,oakUnitCode=(.*),ou=units,dc=oak,dc=ox,dc=ac,dc=uk$', oak_itss_for)
            if match:
                groups.add('itss')
                groups.add('itss:{}'.format(match.group(1)))

        # Remove any old groups with prefixes this backend manages
        user.groups.remove(*user.groups.exclude(name__in=groups).filter(Q(name='itss') | Q(name__startswith='itss:') |
                                                                        Q(name__startswith='affiliation:') |
                                                                        Q(name__startswith='status:')))
        # And add all the new groups
        user.groups.add(*[Group.objects.get_or_create(name=g)[0] for g in groups])
