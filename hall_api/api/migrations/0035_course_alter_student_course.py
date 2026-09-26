from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_student'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='Course',
                    fields=[
                        (
                            'id',
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name='ID'
                            ),
                        ),
                        (
                            'course_name',
                            models.CharField(max_length=100)
                        ),
                        (
                            'duration',
                            models.IntegerField()
                        ),
                    ],
                ),
                migrations.AlterField(
                    model_name='student',
                    name='course',
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='api.course',
                    ),
                ),
            ],
        ),
    ]