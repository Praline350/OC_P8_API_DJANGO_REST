from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import unittest
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from projects.models import Project, Contributor, Issue, Comment

User = get_user_model()

class ProjectTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.another_user = User.objects.create_user(username='anotheruser', password='password')
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.create_project_with_contributors()

    def create_project_with_contributors(self):
        # Création d'un projet et ajout des contributeurs
        project = Project.objects.create(name='Test Project', description='This is a test project', type='back-end', author=self.user)
        Contributor.objects.create(user=self.other_user, project=project)
        return project

    def test_create_project(self):
        Project.objects.all().delete()
        url = reverse('project-list')
        data = {
            'name': 'Test Project',
            'description': 'This is a test project',
            'type': 'back-end',
            'contributors': [self.other_user]
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
            'contributors': ['inexistantUser']  
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
            'contributors': ['testuser','otheruser', 'testuser', 'otheruser']  # Duplication du même ID
        }
        project = Project.objects.get(name='Test Project')
        contributors = Contributor.objects.filter(project=project)
        self.assertEqual(contributors.count(), 2)
        self.assertTrue(contributors.filter(user=self.user).exists())
        self.assertTrue(contributors.filter(user=self.other_user).exists())

    def test_update_project(self):
        project = self.create_project_with_contributors()
        url = reverse('project-detail', args=[project.id])
        data = {
            'name': 'Updated Project',
            'description': 'This is an updated project description',
            'type': 'front-end',
            'contributors': ['anotheruser']
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        project.refresh_from_db()
        self.assertEqual(project.name, 'Updated Project')
        self.assertEqual(project.description, 'This is an updated project description')
        self.assertEqual(project.type, 'front-end')
        self.assertTrue(Contributor.objects.filter(project=project, user=self.user).exists())
        self.assertTrue(Contributor.objects.filter(project=project, user=self.another_user).exists())
        self.assertFalse(Contributor.objects.filter(project=project, user=self.other_user).exists())

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
        response = self.client.patch(url, data)
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

    @classmethod
    def tearDownClass(cls):
        super(ProjectTest, cls).tearDownClass()
        print('Test Project ok')

class IssueTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.not_contributor_user = User.objects.create_user(username='not_contributor', password='password')

        self.project = Project.objects.create(
            name='Test Project',
            description='This is a test project',
            type='back-end',
            author=self.user
            )
        
        self.other_contributor = Contributor.objects.create(user=self.other_user, project=self.project)
        self.project_author = self.project.contributor_set.get(user=self.user)

        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def create_issue(self):
        self.issue = Issue.objects.create(
            project=self.project,
            author=self.project_author,
            title='Test Issue',
            description='This is a test issue',
            status='to-do',
            priority='medium',
            tag='task'
        )
        return self.issue

    def test_get_issue_by_contributor(self):
        issue = self.create_issue()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(RefreshToken.for_user(self.other_user).access_token))
        url = reverse('issue-detail', kwargs={'project_pk': self.project.id, 'pk': issue.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], issue.title)

    def test_get_issue_by_non_contributor(self):
        issue = self.create_issue()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(RefreshToken.for_user(self.not_contributor_user).access_token))
        url = reverse('issue-detail', kwargs={'project_pk': self.project.id, 'pk': issue.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_issue(self):
        url = reverse('issue-list', kwargs={'project_pk': self.project.id})
        data = {
            'title': 'Test Issue',
            'description': 'This is a test issue',
            'status': 'to-do',
            'priority': 'medium',
            'tag': 'task'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        issue = Issue.objects.get(title='Test Issue')
        contributor = Contributor.objects.get(user=self.user, project=self.project)
        self.assertEqual(issue.author, contributor)
        self.assertEqual(issue.project, self.project)
        self.assertEqual(issue.assignees.count(), 0)

    def test_create_issue_by_no_Contributor(self):
        issue = self.create_issue()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(RefreshToken.for_user(self.not_contributor_user).access_token))
        url = reverse('issue-detail', kwargs={'project_pk': self.project.id, 'pk': issue.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_by_author(self):
        issue = self.create_issue()
        url = reverse('issue-detail', kwargs={'project_pk': self.project.id, 'pk': issue.id})
        data = {
            'assignees': [self.other_user.id],
            'description':'Update test'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        issue.refresh_from_db()
        self.assertEqual(issue.assignees.count(), 1)
        self.assertEqual(issue.assignees.first().user, self.other_user)

    def test_update_by_contributor(self):
        issue = self.create_issue()
        url = reverse('issue-detail', kwargs={'project_pk': self.project.id, 'pk': issue.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(RefreshToken.for_user(self.other_user).access_token))
        data = {
            'description': 'not permission'
        }
        response = self.client.patch(url, data)
        issue.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(issue.description, 'This is a test issue')

    def test_update_by_no_contributor(self):
        issue = self.create_issue()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(RefreshToken.for_user(self.not_contributor_user).access_token))
        url = reverse('issue-detail', kwargs={'project_pk': self.project.id, 'pk': issue.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        data = {
            'description': 'not permission'
        }
        response = self.client.patch(url, data)
        issue.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(issue.description, 'This is a test issue')

    def test_delete_by_author(self):
        issue = self.create_issue()
        url = reverse('issue-detail', kwargs={'project_pk': self.project.id, 'pk': issue.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_delete_by_no_author(self):
        issue = self.create_issue()
        url = reverse('issue-detail', kwargs={'project_pk': self.project.id, 'pk': issue.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(RefreshToken.for_user(self.not_contributor_user).access_token))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(RefreshToken.for_user(self.other_user).access_token))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    @classmethod
    def tearDownClass(cls):
        super(IssueTest, cls).tearDownClass()
        print('Test Issue ok')

class CommentTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.no_contributor = User.objects.create_user(username='no_contributor', password='password')
        
        self.project = Project.objects.create(
            name='Test Project',
            description='This is a test project',
            type='back-end',
            author=self.user
        )
        
        Contributor.objects.create(user=self.other_user, project=self.project)
        
        self.issue = Issue.objects.create(
            project=self.project,
            author=Contributor.objects.get(user=self.user, project=self.project),
            title='Test Issue',
            description='This is a test issue',
            status='to-do',
            priority='medium',
            tag='task'
        )
        
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def create_comment(self):
        comment = Comment.objects.create(
            issue=self.issue,
            author=Contributor.objects.get(user=self.user, project=self.project),
            description='Test comment'
        )
        return comment 

    def test_create_comment(self):
        url = reverse('comment-list', kwargs={'project_pk': self.project.id, 'issue_pk': self.issue.id})
        data = {
            'description': 'This is a test comment'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().description, 'This is a test comment')

    def test_create_comment_by_no_contributor(self):
        url = reverse('comment-list', kwargs={'project_pk': self.project.id, 'issue_pk': self.issue.id})
        self.token = str(RefreshToken.for_user(self.no_contributor).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        data = {
            'description': 'This is a test comment'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.count(), 0)

    def test_get_comment_by_contributor(self):
        comment = self.create_comment()
        url = reverse('comment-list', kwargs={'project_pk': self.project.id, 'issue_pk': self.issue.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_comment_by_author(self):
        comment = self.create_comment()
        url = reverse('comment-detail', kwargs={'project_pk': self.project.id, 'issue_pk': self.issue.id, 'pk': comment.id})
        data = {
            'description': 'Updated comment'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.description, 'Updated comment')

    def test_update_by_no_author(self):
        comment = self.create_comment()
        url = reverse('comment-detail', kwargs={'project_pk': self.project.id, 'issue_pk': self.issue.id, 'pk': comment.id})
        self.token = str(RefreshToken.for_user(self.other_user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        data = {
            'description': 'Updated comment'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertEqual(comment.description, 'Test comment')

    def test_delete_comment_by_author(self):
        comment = self.create_comment()
        url = reverse('comment-detail', kwargs={'project_pk': self.project.id, 'issue_pk': self.issue.id, 'pk': comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Comment.objects.count(), 0)

    def test_delete_comment_by_no_author(self):
        comment = self.create_comment()
        url = reverse('comment-detail', kwargs={'project_pk': self.project.id, 'issue_pk': self.issue.id, 'pk': comment.id})
        self.token = str(RefreshToken.for_user(self.other_user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.count(), 1)


    @classmethod
    def tearDownClass(cls):
        super(CommentTest, cls).tearDownClass()
        print('Test Comment ok')

    
        

    