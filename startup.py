import os
import sys
import subprocess

# Do NOT import django here. It might not be installed yet.

def install_requirements():
    print("Installing requirements...")
    # startup.py is outside krs_mekbat, so requirements is in krs_mekbat/requirements.txt
    req_file = os.path.join(os.getcwd(), 'krs_mekbat', 'requirements.txt')
    if os.path.exists(req_file):
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_file])
            print("Requirements installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing requirements: {e}")
            sys.exit(1)
    else:
        print(f"Requirements file not found at {req_file}")
        # Try to find it in current dir just in case
        if os.path.exists('requirements.txt'):
             print("Found requirements.txt in current directory. Installing...")
             subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def setup():
    # 1. Install requirements
    install_requirements()

    # 2. Setup Django Path
    # startup.py is at Root, manage.py is at Root/krs_mekbat/manage.py
    project_path = os.path.join(os.getcwd(), 'krs_mekbat')
    if project_path not in sys.path:
        sys.path.insert(0, project_path)
        print(f"Added {project_path} to sys.path")
    
    # 3. Setup Django Environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'krs_mekbat.settings')
    
    # 4. Import Django NOW
    try:
        import django
        from django.core.management import call_command
        from django.contrib.auth import get_user_model
        
        django.setup()
        print("Django setup successful.")
    except ImportError as e:
        print(f"Error importing Django after installation: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error setting up Django: {e}")
        sys.exit(1)

    print("Running migrations...")
    call_command('migrate')

    print("Running initial data setup...")
    try:
        import setup_initial_data
        setup_initial_data.setup()
    except ImportError:
        print("Warning: setup_initial_data.py not found. Skipping initial data setup.")
    except Exception as e:
        print(f"Error running initial data setup: {e}")


    print("Collecting static files...")
    call_command('collectstatic', interactive=False)

    User = get_user_model()
    # Get credentials from environment variables
    username = os.environ.get('SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('SUPERUSER_EMAIL', 'admin@hmtaupnvy.com')
    password = os.environ.get('SUPERUSER_PASSWORD', 'password')

    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser {username}...")
        User.objects.create_superuser(username, email, password)
        print("Superuser created successfully.")
    else:
        print(f"Superuser {username} already exists.")
    
    print("Setup completed successfully.")

if __name__ == '__main__':
    setup()
