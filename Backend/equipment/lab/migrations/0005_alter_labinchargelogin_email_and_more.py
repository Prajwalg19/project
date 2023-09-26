# Generated by Django 4.1.4 on 2023-09-20 17:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("lab", "0004_labinchargelogin"),
    ]

    operations = [
        migrations.AlterField(
            model_name="labinchargelogin",
            name="email",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="lab_incharge_login_emails",
                to="lab.labinchargeregister",
            ),
        ),
        migrations.AlterField(
            model_name="labinchargelogin",
            name="password",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="lab_incharge_login_passwords",
                to="lab.labinchargeregister",
            ),
        ),
    ]