from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_personnel_phone_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='hall',
            name='additional_services',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
