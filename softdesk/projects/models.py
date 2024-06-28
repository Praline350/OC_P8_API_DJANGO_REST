import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings



TYPE_CHOICES = [
    ('back-end', 'Back-end'),
    ('front-end', 'Front-end'),
    ('ios', 'iOS'),
    ('android', 'Android')
]

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'), 
    ('high', 'High')
]

STATUS_CHOICES = [
    ('to-do', 'To DO'),
    ('in-progress', 'In Progress'),
    ('finished', 'Finished')
]

TAG_CHOICES = [
    ('bug', 'Bug'),
    ('task', 'Task'),
    ('feature', 'Feature')
]


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_projects')
    contributors = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Contributor', related_name='contributed_projects')
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Contributor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.project.name}"


class Issue(models.Model):
    project =  models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    author = models.ForeignKey(Contributor, on_delete=models.CASCADE ,related_name='authored_issues')
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    assignees = models.ManyToManyField(Contributor, related_name='assigned_issues')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES)
    tag = models.CharField(max_length=50, choices=TAG_CHOICES)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.project.name} - {self.title}"
    

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(Contributor, on_delete=models.CASCADE, related_name='comments')
    description = models.TextField(max_length=300)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.user.username} - {self.description[:20]}"





    



