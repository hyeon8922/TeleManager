# Generated by Django 5.0 on 2024-01-03 01:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("client", "0003_remove_client_is_approved"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Marketing",
        ),
    ]