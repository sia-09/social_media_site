# Generated by Django 5.2 on 2025-04-10 15:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_rename_follow_follower_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='follower',
            old_name='followed_at',
            new_name='created_at',
        ),
    ]
