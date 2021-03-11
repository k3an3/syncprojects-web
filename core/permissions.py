from django.contrib.auth.mixins import UserPassesTestMixin


class UserHasObjectPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.coreuser.has_member_access(self.get_object())
