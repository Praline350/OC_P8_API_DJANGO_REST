from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from projects.models import Project, Contributor

User = get_user_model()

class ProjectTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.another_user = User.objects.create_user(username='anotheruser', password='password')
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.create_project_with_contributors()

    def create_project_with_contributors(self):
        # Création d'un projet et ajout des contributeurs

        project = Project.objects.create(name='Test Project', description='This is a test project', type='back-end', author=self.user)
        Contributor.objects.create(user=self.user, project=project)
        Contributor.objects.create(user=self.other_user, project=project)
        return project

    def test_create_project(self):
        Project.objects.all().delete()
        url = reverse('project-list')
        data = {
            'name': 'Test Project',
            'description': 'This is a test project',
            'type': 'back-end',
            'contributors': [self.other_user.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        project = Project.objects.get()
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(project.description, 'This is a test project')
        self.assertEqual(project.type, 'back-end')
        self.assertEqual(project.author, self.user)
        self.assertTrue(Contributor.objects.filter(project=project, user=self.user).exists())
        self.assertTrue(Contributor.objects.filter(project=project, user=self.other_user).exists())

    def test_create_project_with_invalid_contributors(self):
        url = reverse('project-list')
        data = {
            'name': 'Invalid Contributors Project',
            'description': 'This project has invalid contributors',
            'type': 'back-end',
            'contributors': [9999]  # ID d'utilisateur inexistant
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('contributors', response.data)

    def test_create_project_with_duplicate_contributors(self):
        url = reverse('project-list')
        data = {
            'name': 'Duplicate Contributors Project',
            'description': 'This project has duplicate contributors',
            'type': 'back-end',
            'contributors': [self.user.id, self.user.id, self.other_user.id, self.other_user.id]  # Duplication du même ID
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        project = Project.objects.get(name='Duplicate Contributors Project')
        contributors = Contributor.objects.filter(project=project)
        print(response.data)
        self.assertEqual(contributors.count(), 2)
        self.assertEqual(contributors.first().user, self.user)

    def test_update_project_by_author(self):
        project = self.create_project_with_contributors()
        url = reverse('project-detail', args=[project.id])
        data = {
            'name': 'Updated Project',
            'description': 'This is an updated project',
            'type': 'front-end',
            'contributors': [self.other_user.id]
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)
        project.refresh_from_db()
        self.assertEqual(project.name, 'Updated Project')
        self.assertEqual(project.description, 'This is an updated project')
        self.assertEqual(project.type, 'front-end')
        self.assertTrue(Contributor.objects.filter(project=project, user=self.user).exists())
        self.assertTrue(Contributor.objects.filter(project=project, user=self.other_user).exists())
        self.assertFalse(Contributor.objects.filter(project=project, user=self.another_user).exists())

    def test_update_project_by_non_author(self):
        project = self.create_project_with_contributors()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(RefreshToken.for_user(self.other_user).access_token))
        url = reverse('project-detail', args=[project.id])
        data = {
            'name': 'Updated Project',
            'description': 'This is an updated project',
            'type': 'front-end',
            'contributors': [self.user.id]
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(project.name, 'Test Project')

    def test_detail_projects_as_contributor(self):
        project = self.create_project_with_contributors()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(RefreshToken.for_user(self.other_user).access_token))
        url = reverse('project-detail', args=[project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_projects_as_no_contributor(self):
        project = self.create_project_with_contributors()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(RefreshToken.for_user(self.another_user).access_token))
        url = reverse('project-detail', args=[project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_delete_project_by_author(self):
        project = self.create_project_with_contributors()
        url = reverse('project-detail', args=[project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Project.objects.filter(id=project.id).exists())
    
    def test_delete_project_by_no_author(self):
        project = self.create_project_with_contributors()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(RefreshToken.for_user(self.other_user).access_token))
        url = reverse('project-detail', args=[project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Project.objects.filter(id=project.id).exists())