from django.db import migrations


def update_periodic_task(apps, schema_editor):
    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')
    # Find the periodic task created earlier and update its task path
    PeriodicTask.objects.filter(
        name='Delete expired OTPs every 10 minutes'
    ).update(task='accounts.tasks.delete_expired_otps')


def reverse_update(apps, schema_editor):
    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')
    # Revert to previous task name if needed
    PeriodicTask.objects.filter(
        name='Delete expired OTPs every 10 minutes'
    ).update(task='delete_expired_otps_task')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_create_delete_expired_otps_periodic_task'),
        ('django_celery_beat', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_periodic_task, reverse_code=reverse_update),
    ]
