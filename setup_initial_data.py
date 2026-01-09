import os
import sys

def setup():
    """
    Standard script to populate required initial data for krs_mekbat.
    Run this after 'python manage.py migrate'.
    """
    # 1. Setup Django Path
    # This script is at Root, krs_mekbat is a subdir
    project_path = os.path.join(os.getcwd(), 'krs_mekbat')
    if project_path not in sys.path:
        sys.path.insert(0, project_path)
    
    # 2. Setup Django Environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'krs_mekbat.settings')
    
    try:
        import django
        django.setup()
        print("Django environment set up successfully.")
    except Exception as e:
        print(f"Error setting up Django: {e}")
        # Try to provide a hint if it's a path issue
        print("Hint: Check if you are running this script from the project root.")
        sys.exit(1)

    # 3. Import Models
    from war.models import AdminControl

    # 4. Define Requirements
    # List of (name, default_active)
    REQUIRED_CONTROLS = [
        ("register", False),
    ]

    # 5. Execute
    print("Checking required initial data...")
    for name, default_active in REQUIRED_CONTROLS:
        obj, created = AdminControl.objects.get_or_create(
            name=name,
            defaults={'active': default_active}
        )
        if created:
            print(f"[CREATED] AdminControl: '{name}' (Active: {default_active})")
        else:
            print(f"[EXISTS] AdminControl: '{name}'")

    print("\nInitial data setup completed.")

if __name__ == '__main__':
    setup()
