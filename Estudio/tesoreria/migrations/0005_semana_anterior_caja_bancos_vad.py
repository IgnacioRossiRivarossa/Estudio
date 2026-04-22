from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tesoreria', '0004_fci_semana_anterior'),
    ]

    operations = [
        migrations.AddField(
            model_name='caja',
            name='saldo_sem_ant',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='monedaextranjera',
            name='saldo_dolares_sem_ant',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='banco',
            name='saldo_sem_ant_pesos',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='banco',
            name='saldo_usd_sem_ant',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.CreateModel(
            name='ValorADepositarEmpresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('empresa', models.CharField(choices=[('L1', 'L1'), ('L2', 'L2')], max_length=2, unique=True)),
                ('saldo_sem_ant', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
            ],
            options={
                'verbose_name': 'VAD Empresa Sem. Ant.',
                'verbose_name_plural': 'VAD Empresas Sem. Ant.',
            },
        ),
    ]
