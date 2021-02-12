from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from core.models import Project, Lock


class ProjectModelTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="test")
        self.user = User.objects.create(username="tester")

    def test_default_state(self):
        self.assertFalse(self.project.is_locked())
        self.assertFalse(self.project.is_locked_by_user(self.user))

    def test_is_locked(self):
        Lock.objects.create(project=self.project, user=self.user)
        self.assertTrue(self.project.is_locked())

    def test_locked_by_self(self):
        Lock.objects.create(project=self.project, user=self.user)
        self.assertTrue(self.project.is_locked_by_user(self.user))

    def test_locked_by_other(self):
        Lock.objects.create(project=self.project, user=User.objects.create(username="other"))
        self.assertFalse(self.project.is_locked_by_user(self.user))

    def test_lock_expired(self):
        Lock.objects.create(project=self.project, user=self.user, end_time=timezone.now() - timedelta(seconds=15))
        self.assertFalse(self.project.is_locked())
        self.assertTrue(len(self.project.locks()) == 0)

    def test_lock_not_expired(self):
        Lock.objects.create(project=self.project, user=self.user, end_time=timezone.now() + timedelta(seconds=15))
        self.assertTrue(self.project.is_locked())
        self.assertTrue(len(self.project.locks()) == 1)
