from django.contrib.auth.mixins import UserPassesTestMixin

from core.models import Project


class UserIsMemberPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.has_member_access(self.get_object())


class UserIsFollowerOrMemberPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return self.request.user.has_member_access(obj) \
               or self.request.user.has_subscriber_access(obj) \
               and (isinstance(obj, Project) or obj.shared_with_followers)
