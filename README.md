# krs_mekbat
Website that will be used for krs war in Rock Mechanics Lab 2024 and Mine Plan Design Lab 2026

# How to Deploy to Hostinger Server

## 1. Create Python Application
1. Login to your Hostinger cPanel account (or hPanel).
2. Go to **Python App** / **Create Python App**.
3. Click **Create Application**.

### Configuration:
- **Python Version**: Select `3.11`.
- **Application Root**: The folder name where you will upload the project (e.g., `krs_mekbat`).
- **Application URL**: Select your subdomain/domain.
- **Application Startup File**: `passenger_wsgi.py`
- **Application Entry Point**: `application`

## 2. Prepare and Upload Project
1. **Prepare the project folder**:
   - Ensure `manage.py` and `passenger_wsgi.py` are inside your project folder.
   - Zip the contents of your project folder (or the folder itself).
2. **Upload to Hostinger**:
   - Go to File Manager.
   - Navigate to your **root_folder** (e.g., specific to your subdomain or just outside public_html).
   - Create a folder named `krs_mekbat` (This matches your **Application Root**).
   - Upload and extract your project files **inside** this `krs_mekbat` folder.
   - **Structure check**: You should have `root_folder/krs_mekbat/manage.py`.

## 3. Upload Helper Files
Upload the following files to your **root_folder** (the parent directory of `krs_mekbat`, ensuring they are accessible as needed for startup):
*   `passenger_wsgi.py` (Found in project root)
*   `startup.py` (Found in project root)
*   `setup_initial_data.py` (Found in project root)
*   `requirements.txt` (Found in project root)

## 4. Environment Variables
Set your environment variables in the Python App configuration.
**Important Advice**:
- Set `DEBUG` to `0` on production.
- `STATIC_ROOT` should be `/home/hostinger_username/root_folder/public/static`
- `MEDIA_ROOT` should be `/home/hostinger_username/root_folder/public/media`

### Example `.env` Configuration:
```
DEBUG=0

# Hostinger Setup
# Replace 'hostinger_username' and 'root_folder' with your actual paths
STATIC_ROOT=/home/hostinger_username/root_folder/public/static
MEDIA_ROOT=/home/hostinger_username/root_folder/public/media

# Security (Use your real secure keys here)
SECRET_KEY=dummy-secret-key-change-this
ENCRYPTION_KEY=dummy-encryption-key-change-this
API_KEY=dummy-api-key-change-this

# Superuser Configuration
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=change_this_password
```

## 5. Final Setup
1. **Install Dependencies**:
   - In the Python App settings, ensure `requirements.txt` is detected or manually specify it.
   - Run Pip Install.
2. **Execute Startup Script**:
   - In the "Execute python script" section:
   - Enter `startup.py`.
   - Click **Run Script**.

## 6. How to Run Locally

If you want to run the application on your local machine:

1.  **Configure Environment**:
    -   Set `DEBUG=1` in your local `.env` file.

2.  **Full Setup (Fresh Install)**:
    -   If you haven't installed requirements or created a superuser yet, simply run `startup.py`:
        ```bash
        python startup.py
        ```
    -   This script will:
        -   Install dependencies from `requirements.txt`.
        -   Apply database migrations.
        -   Run `setup_initial_data.py` to populate initial database entries.
        -   Collect static files.
        -   Create a default superuser if one doesn't exist.

3.  **Partial Setup (Data Only)**:
    -   If you just want to set up or reset the `AdminControl` database entries without running the full setup, run:
        ```bash
        python setup_initial_data.py
        ```
