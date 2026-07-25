from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blocks',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
