from django.db import models
import uuid

# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length=80, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    project_image = models.ImageField(null=True, blank=True, default='default.jpg')
    demo_link = models.CharField(max_length=2000, blank=True, null=True)
    github_link = models.CharField(max_length=2000, blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    total_vote = models.IntegerField(null=True, blank=True, default=0)
    vote_ratio = models.IntegerField(null=True, blank=True, default=0)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    VOTE_TYPE = (
        ('up', 'Up Vote'),
        ('down', 'Down Vote'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    vote_type = models.CharField(choices=VOTE_TYPE, null=True, blank=True)
    comment = models.TextField(max_length=1600, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)

    def __str__(self):
        return self.vote_type


class Tag(models.Model):
    name = models.CharField(max_length=60, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)

    def __str__(self):
        return str(self.name)