from django.contrib.auth.mixins import UserPassesTestMixin


class UserHasObjectPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.coreuser.has_access_to(self.get_object())
