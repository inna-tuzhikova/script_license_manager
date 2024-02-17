from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return self.name


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

    class Meta:
        ordering = ['name']


class IssuedLicense(models.Model):
    class Action(models.TextChoices):
        GENERATE = 'GENERATE', 'Generate script'
        UPDATE = 'UPDATE', 'Update issued script license'

    class IssueType(models.TextChoices):
        PLAIN = 'PLAIN', 'Script without encoding'
        ENCODED = 'ENCODED', 'Encoded script'
        ENCODED_LK = 'ENCODED_LK', 'Script encoded with a license key'
        ENCODED_EXP = 'ENCODED_EXP', 'Script encoded with an expiration date'
        ENCODED_EXP_LK = (
            'ENCODED_EXP_LK',
            'Script encoded with a license key and expiration date'
        )

    issued_at = models.DateTimeField()
    license_key = models.CharField()
    script = models.ForeignKey(Script, on_delete=models.CASCADE)
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    issue_type = models.CharField(choices=IssueType.choices)
    action = models.CharField(choices=Action.choices)
    demo_lk = models.BooleanField()
    expires = models.DateField(null=True)
    extra_params = models.JSONField(null=True)

    class Meta:
        db_table = 'scripts_issued_license'
        ordering = ['-issued_at']

    def is_permanent(self):
        return self.expires is None
