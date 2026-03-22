How to run the template project?

For EC2 administration, run the following commands to start the server:

```bash
source /venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

For local development:

```bash
python manage.py migrate
python manage.py runserver
```
