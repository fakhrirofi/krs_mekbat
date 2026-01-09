
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'krs_mekbat.settings')
django.setup()

from war.models import UserData

def migrate_data():
    print("Migrating UserData.schedule to UserData.schedules...")
    users = UserData.objects.all()
    count = 0
    for u in users:
        if u.schedule:
            u.schedules.add(u.schedule)
            count += 1
    print(f"Migrated {count} users.")

if __name__ == "__main__":
    migrate_data()
