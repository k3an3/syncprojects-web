from django.contrib.auth.mixins import UserPassesTestMixin


class UserIsMemberPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.coreuser.has_member_access(self.get_object())


class UserIsFollowerOrMemberPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.coreuser.has_member_access(self.get_object()) \
               or self.request.user.coreuser.has_subscriber_access(self.get_object())
