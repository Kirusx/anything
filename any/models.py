from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class ProjectLog(models.Model):
    project_id = models.AutoField(primary_key=True, unique=True)
    project_name = models.CharField(max_length=100)
    project_grey_ip = models.GenericIPAddressField(max_length=32)
    project_online_ip = models.GenericIPAddressField(max_length=32)
    project_dept_name = models.CharField(max_length=100)


class ProjectGroup(models.Model):
    group_id = models.AutoField(primary_key=True, unique=True)
    group_name = models.CharField(max_length=100)
    user = models.ManyToManyField(User)
    log = models.ManyToManyField(ProjectLog)




