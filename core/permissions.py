from django.contrib.auth.mixins import UserPassesTestMixin


class UserHasObjectPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.coreuser.is_member_of(self.get_object())
