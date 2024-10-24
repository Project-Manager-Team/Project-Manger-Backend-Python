# Generated by Django 5.1.1 on 2024-10-12 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='time_end',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='time_start',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='type',
            field=models.CharField(choices=[('project', 'Project'), ('task', 'Task'), ('personal', 'Personal')], default='task', max_length=8),
        ),
    ]
