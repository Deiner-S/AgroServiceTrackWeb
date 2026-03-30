from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("checklist", "0002_address_clientaddress_client_addresses_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employee",
            name="position",
            field=models.CharField(
                choices=[
                    ("0", "Diretor"),
                    ("1", "Gerente"),
                    ("2", "Administrativo"),
                    ("3", "Técnico"),
                ],
                max_length=100,
            ),
        ),
    ]
