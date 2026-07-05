from django.db import migrations


def create_roles(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for role_name in ("teacher", "student"):
        Group.objects.get_or_create(name=role_name)


class Migration(migrations.Migration):
    dependencies = [
        ("quiz_api", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_roles, migrations.RunPython.noop),
    ]
