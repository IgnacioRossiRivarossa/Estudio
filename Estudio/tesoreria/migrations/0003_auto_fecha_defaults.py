import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tesoreria', '0002_add_tipo_to_tituloon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caja',
            name='fecha',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='banco',
            name='fecha',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='monedaextranjera',
            name='fecha',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='valoradepositar',
            name='fecha_carga',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='plazofijo',
            name='fecha_carga',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='fci',
            name='fecha',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='tituloon',
            name='fecha',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
