from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=1000, null=True)


class Category(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = 'categories'


class Script(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    enabled = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    extra_params_schema = models.JSONField(null=True, default=None)
    allow_issue_plain = models.BooleanField(default=True)
    allow_issue_wo_lk = models.BooleanField(default=True)
    allow_issue_w_lk = models.BooleanField(default=True)
    allow_issue_w_expiration = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag)


class IssuedLicense(models.Model):
    class Action(models.TextChoices):
        GENERATE_DEMO_LICENSE = 'GENERATE_DEMO_LICENSE', 'GENERATE_DEMO_LICENSE'
        GENERATE_USER_LICENSE = 'GENERATE_USER_LICENSE', 'GENERATE_USER_LICENSE'
        UPDATE_LICENSE = 'UPDATE_LICENSE', 'UPDATE_LICENSE'

    issued_at = models.DateTimeField()
    license_key = models.CharField()
    script = models.ForeignKey(Script, on_delete=models.CASCADE)
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE)
    demo_lk = models.BooleanField()
    expires = models.DateField(null=True)
    extra_params = models.JSONField(null=True)
    action = models.CharField(choices=Action.choices)

    class Meta:
        db_table = 'scripts_issued_license'
