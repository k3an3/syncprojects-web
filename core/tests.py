from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from core.models import Project, Song, Lock


class ProjectModelTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="test")
        self.user = User.objects.create(username="tester")

    def test_default_state(self):
        self.assertFalse(self.project.is_locked())
        self.assertFalse(self.project.is_locked_by_user(self.user))

    def test_is_locked(self):
        Lock.objects.create(object=self.project, user=self.user)
        self.assertTrue(self.project.is_locked())

    def test_locked_by_self(self):
        Lock.objects.create(object=self.project, user=self.user)
        self.assertTrue(self.project.is_locked_by_user(self.user))

    def test_locked_by_other(self):
        Lock.objects.create(object=self.project, user=User.objects.create(username="other"))
        self.assertFalse(self.project.is_locked_by_user(self.user))

    def test_lock_expired(self):
        Lock.objects.create(object=self.project, user=self.user, end_time=timezone.now() - timedelta(seconds=15))
        self.assertFalse(self.project.is_locked())
        self.assertTrue(len(self.project.locks.all()) == 0)

    def test_lock_not_expired(self):
        Lock.objects.create(object=self.project, user=self.user, end_time=timezone.now() + timedelta(seconds=15))
        self.assertTrue(self.project.is_locked())
        self.assertTrue(len(self.project.locks.all()) == 1)


class CoreUserModelTests(TestCase):
    def setUp(self):
        self.project_1 = Project.objects.create(name="test1")
        self.project_2 = Project.objects.create(name="test1")
        self.song_1 = Song.objects.create(name='foo', project=self.project_1)
        self.song_2 = Song.objects.create(name='bar', project=self.project_2)
        self.user = User.objects.create(username="tester")

    def test_membership(self):
        self.user.coreuser.projects.add(self.project_1)
        self.assertTrue(self.user.coreuser.has_access_to(self.project_1))
        self.assertFalse(self.user.coreuser.has_access_to(self.project_2))

    def test_membership_song(self):
        self.user.coreuser.projects.add(self.project_1)
        self.assertTrue(self.user.coreuser.has_access_to(self.song_1))
        self.assertFalse(self.user.coreuser.has_access_to(self.song_2))

    def test_membership_unhandled_type(self):
        with self.assertRaises(NotImplementedError):
            self.user.coreuser.has_access_to("asdf")


class SongModelTests(TestCase):
    def setUp(self):
        self.project_1 = Project.objects.create(name="test1")
        self.song = Song.objects.create(name='foo', project=self.project_1)
        self.user = User.objects.create(username="tester")

    def test_clear_peaks(self):
        self.song.peaks = 'asdfy'
        self.song.clear_peaks()
        self.assertEquals(self.song.peaks, '')

    def test_default_state(self):
        self.assertFalse(self.song.is_locked())
        self.assertFalse(self.song.is_locked_by_user(self.user))

    def test_is_locked(self):
        Lock.objects.create(object=self.song, user=self.user)
        self.assertTrue(self.song.is_locked())

    def test_locked_by_self(self):
        Lock.objects.create(object=self.song, user=self.user)
        self.assertTrue(self.song.is_locked_by_user(self.user))

    def test_locked_by_other(self):
        Lock.objects.create(object=self.song, user=User.objects.create(username="other"))
        self.assertFalse(self.song.is_locked_by_user(self.user))

    def test_lock_expired(self):
        Lock.objects.create(object=self.song, user=self.user, end_time=timezone.now() - timedelta(seconds=15))
        self.assertFalse(self.song.is_locked())
        self.assertTrue(len(self.song.locks.all()) == 0)

    def test_lock_not_expired(self):
        Lock.objects.create(object=self.song, user=self.user, end_time=timezone.now() + timedelta(seconds=15))
        self.assertTrue(self.song.is_locked())
        self.assertTrue(len(self.song.locks.all()) == 1)
