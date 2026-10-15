# Skechers Store

## Run locally on Windows

Use Python 3.10 or newer. From the project folder, run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser. To create an admin account, run
`python manage.py createsuperuser` and visit <http://127.0.0.1:8000/admin/>.

The development server and the default SQLite database are for local development,
not public production hosting.
