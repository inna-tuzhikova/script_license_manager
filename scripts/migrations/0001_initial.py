# Generated by Django 5.0.2 on 2024-02-17 16:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def pre_populate_cats_and_tags(apps, schema_editor):
    Tag = apps.get_model('scripts', 'Tag')
    Category = apps.get_model('scripts', 'Category')

    Tag.objects.create(
        name='archived',
        description='Archived scripts that are no longer supported'
    )
    paid = Category.objects.create(
        id='paid',
        name='Paid scripts',
        description='Paid scripts',
        parent=None
    )
    Category.objects.create(
        id='bi_modules',
        name='BI Modules',
        description='BI Modules',
        parent=paid
    )
    Category.objects.create(
        id='paid_scripts',
        name='Paid scripts',
        description='Paid scripts',
        parent=paid
    )

    free = Category.objects.create(
        id='free',
        name='Free scripts',
        description='Free scripts',
        parent=None
    )
    Category.objects.create(
        id='free_scripts',
        name='Free scripts',
        description='Free scripts',
        parent=free
    )
    Category.objects.create(
        id='resources',
        name='Resources',
        description='Resources',
        parent=free
    )

    Category.objects.create(
        id='internal',
        name='Internal scripts',
        description='Internal scripts',
        parent=None
    )
    Category.objects.create(
        id='projects',
        name='Projects scripts',
        description='Projects scripts',
        parent=None
    )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=1000)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='scripts.category')),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=1000)),
                ('enabled', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('extra_params_schema', models.JSONField(default=None, null=True)),
                ('allow_issue_plain', models.BooleanField(default=True)),
                ('allow_issue_wo_lk', models.BooleanField(default=True)),
                ('allow_issue_w_lk', models.BooleanField(default=True)),
                ('allow_issue_w_expiration', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scripts.category')),
                ('tags', models.ManyToManyField(to='scripts.tag')),
            ],
        ),
        migrations.CreateModel(
            name='IssuedLicense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issued_at', models.DateTimeField()),
                ('license_key', models.CharField()),
                ('demo_lk', models.BooleanField()),
                ('expires', models.DateField(null=True)),
                ('extra_params', models.JSONField(null=True)),
                ('action', models.CharField(choices=[('GENERATE_DEMO_LICENSE', 'GENERATE_DEMO_LICENSE'), ('GENERATE_USER_LICENSE', 'GENERATE_USER_LICENSE'), ('UPDATE_LICENSE', 'UPDATE_LICENSE')])),
                ('issued_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('script', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scripts.script')),
            ],
            options={
                'db_table': 'issued_license',
            },
        ),
        migrations.RunPython(
            code=pre_populate_cats_and_tags,
        ),
        migrations.AlterModelTable(
            name='issuedlicense',
            table='scripts_issued_license',
        ),
    ]
