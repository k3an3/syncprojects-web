from datetime import timedelta

from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.views.generic import TemplateView

from core.models import Project, Song, Lock
from core.permissions import UserIsMemberPermissionMixin, UserIsFollowerOrMemberPermissionMixin
from core.s3 import PRESIGNED_URL_DURATION, FAILURE_RETRY_INTERVAL
from core.views import ProjectDetailView
from users.models import User


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
        Lock.objects.create(object=self.project, user=User.objects.create(email="other"))
        self.assertFalse(self.project.is_locked_by_user(self.user))

    def test_lock_expired(self):
        Lock.objects.create(object=self.project, user=self.user, end_time=timezone.now() - timedelta(seconds=15))
        self.assertFalse(self.project.is_locked())
        self.assertTrue(len(self.project.locks.all()) == 0)

    def test_lock_not_expired(self):
        Lock.objects.create(object=self.project, user=self.user, end_time=timezone.now() + timedelta(seconds=15))
        self.assertTrue(self.project.is_locked())
        self.assertTrue(len(self.project.locks.all()) == 1)

    def test_unlock(self):
        Lock.objects.create(object=self.project, user=self.user, end_time=timezone.now() + timedelta(seconds=15))
        self.project.unlock()
        self.assertFalse(self.project.is_locked())


class CoreUserModelTests(TestCase):
    def setUp(self):
        self.project_1 = Project.objects.create(name="test1")
        self.project_2 = Project.objects.create(name="test1")
        self.song_1 = Song.objects.create(name='foo', project=self.project_1)
        self.song_2 = Song.objects.create(name='bar', project=self.project_2)
        self.user = User.objects.create(username="tester")

    def test_membership(self):
        self.user.projects.add(self.project_1)
        self.assertTrue(self.user.has_member_access(self.project_1))
        self.assertFalse(self.user.has_member_access(self.project_2))

    def test_membership_song(self):
        self.user.projects.add(self.project_1)
        self.assertTrue(self.user.has_member_access(self.song_1))
        self.assertFalse(self.user.has_member_access(self.song_2))

    def test_membership_unhandled_type(self):
        with self.assertRaises(NotImplementedError):
            self.user.has_member_access("asdf")


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
        Lock.objects.create(object=self.song, user=User.objects.create(email="other_2"))
        self.assertFalse(self.song.is_locked_by_user(self.user))

    def test_lock_expired(self):
        Lock.objects.create(object=self.song, user=self.user, end_time=timezone.now() - timedelta(seconds=15))
        self.assertFalse(self.song.is_locked())
        self.assertTrue(len(self.song.locks.all()) == 0)

    def test_lock_not_expired(self):
        Lock.objects.create(object=self.song, user=self.user, end_time=timezone.now() + timedelta(seconds=15))
        self.assertTrue(self.song.is_locked())
        self.assertTrue(len(self.song.locks.all()) == 1)

    def test_unlock(self):
        Lock.objects.create(object=self.song, user=self.user, end_time=timezone.now() + timedelta(seconds=15))
        self.song.unlock()
        self.assertFalse(self.song.is_locked())

    def test_signed_url_default(self):
        self.assertTrue(self.song.should_fetch_url())

    def test_signed_url_too_recent(self):
        self.song.url_last_fetched = timezone.now()
        self.assertFalse(self.song.should_fetch_url())

    def test_signed_url_should_1(self):
        self.song.url_last_fetched = timezone.now() - timedelta(seconds=PRESIGNED_URL_DURATION)
        self.assertTrue(self.song.should_fetch_url())

    def test_signed_url_error_too_recent(self):
        self.song.url_last_error = timezone.now()
        self.assertFalse(self.song.should_fetch_url())

    def test_signed_url_error_should(self):
        self.song.url_last_error = timezone.now() - timedelta(seconds=FAILURE_RETRY_INTERVAL)
        self.assertTrue(self.song.should_fetch_url())


class DummyViewFactory:
    @staticmethod
    def make(mixin):
        class Dummy(mixin, TemplateView):
            template_name = 'any_template.html'  # TemplateView requires this attribute

            def __init__(self, obj, user):
                super().__init__()
                self.object = obj
                self.get_object = lambda: self.object
                self.request = RequestFactory().get('/nonexistent')
                self.request.user = user

        return Dummy


class ProjectDetailViewTests(TestCase):
    def setUp(self):
        self.view = DummyViewFactory.make(ProjectDetailView)
        self.project = Project.objects.create(name="test1")
        self.song_1 = Song.objects.create(name='foo', project=self.project)
        self.song_2 = Song.objects.create(name='foo2', project=self.project)
        self.user = User.objects.create(username="tester")

    def test_no_access(self):
        self.assertFalse(self.view(self.project, self.user).get_context_data()['songs'])
        self.assertFalse(self.view(self.project, self.user).get_context_data()['member'])

    def test_song_list_member(self):
        self.user.projects.add(self.project)
        self.assertEqual(self.view(self.project, self.user).get_context_data()['songs'], [self.song_1, self.song_2])
        self.assertTrue(self.view(self.project, self.user).get_context_data()['member'])

    def test_partial_song_list_follower(self):
        self.user.subscribed_projects.add(self.project)
        self.song_2.shared_with_followers = True
        self.song_2.save()
        self.assertFalse(self.view(self.project, self.user).get_context_data()['member'])
        self.assertEqual(self.view(self.project, self.user).get_context_data()['songs'], [self.song_2])


class UserIsMemberTests(TestCase):
    def setUp(self):
        self.view = DummyViewFactory.make(UserIsMemberPermissionMixin)
        self.project = Project.objects.create(name="test1")
        self.song = Song.objects.create(name='foo', project=self.project)
        self.user = User.objects.create(username="tester")

    def test_user_is_not_project_member(self):
        self.assertFalse(self.view(self.project, self.user).test_func())

    def test_user_is_project_member(self):
        self.user.projects.add(self.project)
        self.assertTrue(self.view(self.project, self.user).test_func())

    def test_user_is_not_song_member(self):
        self.assertFalse(self.view(self.song, self.user).test_func())

    def test_user_is_song_member(self):
        self.user.projects.add(self.project)
        self.assertTrue(self.view(self.song, self.user).test_func())


class UserIsFollowerOrMemberTests(TestCase):
    def setUp(self):
        self.view = DummyViewFactory.make(UserIsFollowerOrMemberPermissionMixin)
        self.project = Project.objects.create(name="test1")
        self.song = Song.objects.create(name='foo', project=self.project)
        self.user = User.objects.create(username="tester")

    def test_no_access(self):
        self.assertFalse(self.view(self.project, self.user).test_func())

    def test_has_follower_access(self):
        self.user.subscribed_projects.add(self.project)
        self.assertTrue(self.view(self.project, self.user).test_func())

    def test_has_member_access(self):
        self.user.projects.add(self.project)
        self.assertTrue(self.view(self.project, self.user).test_func())

    def test_no_song_access(self):
        self.assertFalse(self.view(self.song, self.user).test_func())

    def test_no_song_access_as_follower(self):
        self.user.subscribed_projects.add(self.project)
        self.assertFalse(self.view(self.song, self.user).test_func())

    def test_allowed_song_access_as_follower(self):
        self.user.subscribed_projects.add(self.project)
        self.song.shared_with_followers = True
        self.assertTrue(self.view(self.song, self.user).test_func())

    def test_song_access_as_member(self):
        self.user.projects.add(self.project)
        self.assertTrue(self.view(self.song, self.user).test_func())
