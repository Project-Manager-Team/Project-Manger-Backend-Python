# Generated by Django 5.1.1 on 2024-11-01 17:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_rename_time_send_invitation_sendtime'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='initTime',
            new_name='iniTime',
        ),
    ]
