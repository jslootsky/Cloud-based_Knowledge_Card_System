# Generated migration to add histogram_signature field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cards", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="cardimage",
            name="histogram_signature",
            field=models.TextField(blank=True, default=""),
        ),
    ]
