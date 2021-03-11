from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

# Create your tests here.
from sync.models import ClientUpdate


class ClientUpdateModelTests(TestCase):
    def setUp(self):
        self.update = ClientUpdate(version='1.0', _updater=SimpleUploadedFile('updater', b''),
                                   package=SimpleUploadedFile('packager', b''))

    def test_update(self):
        self.assertEquals()
