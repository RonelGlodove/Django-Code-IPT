from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_create_user_profiles_for_existing_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='age',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='birthday',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='place',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
