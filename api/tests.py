from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from api.project.models import Project
from api.permissions.models import Permissions

class PermissionsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='tester', password='testpass')
        self.client.login(username='tester', password='testpass')
        self.project = Project.objects.create(title='Test Project', owner=self.user)

    def test_create_permission(self):
        response = self.client.post('/api/permissions/permissions/', {
            'project_id': self.project.id,
            'user_id': self.user.id,
            'canEdit': True,
            'canDelete': False,
            'canAdd': True,
            'canFinish': False
        })
        self.assertEqual(response.status_code, 201)