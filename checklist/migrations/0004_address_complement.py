from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("checklist", "0003_alter_employee_position_choices"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="complement",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
