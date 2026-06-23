# PythonAnywhere Deployment

This project is deployed as one Django web app:

- Django serves `/api/v1/` and `/admin/`.
- Django returns `frontend/dist/index.html` for Vue history routes.
- PythonAnywhere serves `/assets/` from `frontend/dist/assets`.
- PythonAnywhere serves `/static/` from `backend/staticfiles`.

Replace `yourusername` with your PythonAnywhere username in all commands.

For the `linkukai` PythonAnywhere account, reuse the existing old free-account MySQL database:

```text
linkukai$default
```

Do not delete the `default` database unless you are certain PythonAnywhere lets you recreate it.

## 1. Clean Old PythonAnywhere Content Safely

Before deleting anything, make backups from a PythonAnywhere Bash console:

```bash
cd ~
mkdir -p backups
tar -czf backups/old-home-$(date +%Y%m%d).tar.gz --exclude=backups .
```

If you have an old MySQL database, back it up first:

```bash
mysqldump -u yourusername -h yourusername.mysql.pythonanywhere-services.com -p 'yourusername$old_database' > backups/old_database.sql
```

Then clear old project files only after you are sure the backup is good:

```bash
rm -rf ~/old_project_folder
rm -rf ~/.virtualenvs/old_virtualenv
```

To remove an old web app, use the PythonAnywhere **Web** tab and delete the existing web app. To delete an old database, open a MySQL console and run:

```sql
drop database `yourusername$old_database`;
```

Deletion is irreversible, so do not run these cleanup commands until you are ready.

## 2. Upload Code

Recommended:

```bash
cd ~
git clone https://github.com/your-github-user/Bookstore.git
cd Bookstore
```

If the repo is not on GitHub, upload the folder through PythonAnywhere's **Files** page.

## 3. Create Virtualenv

Use a Python version available in your PythonAnywhere account:

```bash
mkvirtualenv --python=/usr/bin/python3.12 bookstore-venv
cd ~/Bookstore
pip install -r backend/requirements.txt
```

If Python 3.12 is not available, use the newest Python shown in the PythonAnywhere virtualenv picker.

## 4. Configure Environment

Create the production environment file:

```bash
cp backend/.env.pythonanywhere.example backend/.env
nano backend/.env
```

Set:

- `ALLOWED_HOSTS=yourusername.pythonanywhere.com`
- `DB_HOST` from the PythonAnywhere **Databases** tab
- `DB_NAME=yourusername$online_bookstore_db`
- `DB_USER=yourusername`
- `DB_PASSWORD` to your PythonAnywhere MySQL password
- strong random values for `SECRET_KEY` and `JWT_SECRET_KEY`

## 5. Create And Load MySQL Database

In the PythonAnywhere **Databases** tab, create:

```text
online_bookstore_db
```

The real database name will be:

```text
yourusername$online_bookstore_db
```

Then import schema and sample data from Bash:

```bash
mysql -u yourusername -h yourusername.mysql.pythonanywhere-services.com -p 'yourusername$online_bookstore_db' < sql/create_tables.sql
mysql -u yourusername -h yourusername.mysql.pythonanywhere-services.com -p 'yourusername$online_bookstore_db' < sql/insert_sample_data.sql
mysql -u yourusername -h yourusername.mysql.pythonanywhere-services.com -p 'yourusername$online_bookstore_db' < sql/views_or_reports.sql
```

For `linkukai`, use the existing `linkukai$default` database and skip the `USE online_bookstore_db;` line that appears in the SQL files:

```bash
grep -v '^USE ' sql/create_tables.sql | mysql -u linkukai -h linkukai.mysql.pythonanywhere-services.com -p 'linkukai$default'
grep -v '^USE ' sql/insert_sample_data.sql | mysql -u linkukai -h linkukai.mysql.pythonanywhere-services.com -p 'linkukai$default'
grep -v '^USE ' sql/views_or_reports.sql | mysql -u linkukai -h linkukai.mysql.pythonanywhere-services.com -p 'linkukai$default'
```

Then run Django checks:

```bash
cd ~/Bookstore
python backend/manage.py check
python backend/manage.py collectstatic --noinput
```

## 6. Build Frontend

You can build locally and upload `frontend/dist`, or build on PythonAnywhere if `node`/`npm` are available:

```bash
cd ~/Bookstore/frontend
npm ci
npm run build
```

The app expects API requests under `/api/v1`, so no separate frontend server is needed in production.

## 7. Configure Web App

In PythonAnywhere **Web** tab:

1. Create a new web app.
2. Choose **Manual Configuration**, not the Django starter template.
3. Select the same Python version as your virtualenv.
4. Set **Virtualenv** to:

```text
/home/yourusername/.virtualenvs/bookstore-venv
```

5. Set **Source code** and **Working directory** to:

```text
/home/yourusername/Bookstore
```

6. Edit the WSGI file, replacing its contents with:

```python
import os
import sys

path = "/home/yourusername/Bookstore/backend"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 8. Configure Static Files

In PythonAnywhere **Web** tab, add static mappings:

```text
/static/  ->  /home/yourusername/Bookstore/backend/staticfiles
/assets/  ->  /home/yourusername/Bookstore/frontend/dist/assets
```

Reload the web app.

## 9. Verify

Open:

```text
https://yourusername.pythonanywhere.com/
```

If the site errors, check the error log link in the PythonAnywhere **Web** tab first.
