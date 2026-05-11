from django.db import migrations


def create_periodic_task(apps, schema_editor):
    # Use the historical models API
    IntervalSchedule = apps.get_model('django_celery_beat', 'IntervalSchedule')
    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')

    # Create or get interval schedule for every 10 minutes
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=10,
        period='minutes',
    )

    # Create the periodic task if not exists
    PeriodicTask.objects.get_or_create(
        interval=schedule,
        name='Delete expired OTPs every 10 minutes',
        task='accounts.tasks.delete_expired_otps',
        defaults={
            'enabled': True,
        }
    )


def remove_periodic_task(apps, schema_editor):
    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')
    PeriodicTask.objects.filter(name='Delete expired OTPs every 10 minutes').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('django_celery_beat', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_periodic_task, reverse_code=remove_periodic_task),
    ]
