from django.contrib.auth.mixins import UserPassesTestMixin

from core.models import Project


class UserIsMemberPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.coreuser.has_member_access(self.get_object())


class UserIsFollowerOrMemberPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.coreuser.has_member_access(self.get_object()) \
               or self.request.user.coreuser.has_subscriber_access(self.get_object()) \
               and (isinstance(self.get_object(), Project) or self.get_object().shared_with_followers)
