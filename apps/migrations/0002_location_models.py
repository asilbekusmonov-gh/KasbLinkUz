# Generated manually for geographic city/district refactor

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apps", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="city",
            name="worker",
        ),
        migrations.AddField(
            model_name="workerprofile",
            name="service_districts",
            field=models.ManyToManyField(
                blank=True,
                related_name="workers",
                to="apps.district",
            ),
        ),
    ]
