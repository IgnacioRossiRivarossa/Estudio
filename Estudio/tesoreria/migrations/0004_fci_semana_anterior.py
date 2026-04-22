from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tesoreria', '0003_auto_fecha_defaults'),
    ]

    operations = [
        migrations.AddField(
            model_name='fci',
            name='cuotapartes_sem_ant',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='fci',
            name='saldo_sem_ant',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
    ]
