from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from sync.models import ClientUpdate


class ClientUpdateModelTests(TestCase):
    def setUp(self):
        self.update = ClientUpdate.objects.create(version='1.0', updater=SimpleUploadedFile('updater_test123', b''),
                                                  package=SimpleUploadedFile('packager', b''))

    def test_update(self):
        self.assertTrue('updater_test123' in self.update.updater.name)

    def test_update_reuse_updater(self):
        update2 = ClientUpdate.objects.create(version='2.0', package=SimpleUploadedFile('packager2', b''))
        self.assertTrue('updater_test123' in update2.latest_updater())

    def test_update_reuse_updater_1(self):
        update2 = ClientUpdate.objects.create(version='2.0', package=SimpleUploadedFile('packager2', b''),
                                              updater=SimpleUploadedFile('updater_test456', b''))
        update3 = ClientUpdate.objects.create(version='2.1', package=SimpleUploadedFile('packager2', b''))
        self.assertTrue('updater_test456' in update3.latest_updater())
