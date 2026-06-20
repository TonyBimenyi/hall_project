import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hall_api.settings")
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT id, app, name, applied FROM django_migrations WHERE app = 'api' ORDER BY id;")
    for row in cursor.fetchall():
        print(row)
