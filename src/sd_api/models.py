import uuid
from django.db import models
from src.sd_auth.models import CustomUser
from django.core import serializers


class Choices:
    # Project type
    BACK_END = 'BAE'
    FRONT_END = 'FRE'
    IOS = 'IOS'
    ANDROID = 'AND'
    PROJECT_TYPE_CHOICES = [
        (BACK_END, 'Back-End'),
        (FRONT_END, 'Front-End'),
        (IOS, 'IOS'),
        (ANDROID, 'Android'),
    ]

    # Issue priority
    LOW = 'LOW'
    MEDIUM = 'MED'
    HIGH = 'HIGH'
    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
    ]

    # Issue tag
    BUG = 'BUG'
    FEATURE = 'FEAT'
    TASK = 'TASK'
    TAG_CHOICES = [
        (BUG, 'Bug'),
        (FEATURE, 'Feature'),
        (TASK, 'Task'),
    ]

    # Issue status
    TODO = 'TODO'
    IN_PROGRESS = 'INPR'
    FINISHED = 'FINI'
    STATUS_CHOICES = [
        (TODO, 'To Do'),
        (IN_PROGRESS, 'In Progress'),
        (FINISHED, 'Finished'),
    ]


class TimestampModel(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class AuthorModel(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='%(class)ss')

    class Meta:
        abstract = True


class Project(TimestampModel, AuthorModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=3, choices=Choices.PROJECT_TYPE_CHOICES)


class Issue(TimestampModel, AuthorModel):
    title = models.CharField(max_length=100)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    assignee = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='assigned_issues')
    priority = models.CharField(max_length=4, choices=Choices.PRIORITY_CHOICES, blank=False)
    tag = models.CharField(max_length=4, choices=Choices.TAG_CHOICES, blank=False)
    status = models.CharField(max_length=4, choices=Choices.STATUS_CHOICES, default=Choices.TODO)


class Comment(TimestampModel, AuthorModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')


class Contributor(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='contributions')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='contributors')
