How to run the template project?

For EC2 administration, run the following commands to start the server:

```bash
# 1. Activate virtual environment
source /venv/bin/activate

# 2. Set environment variables for remote access
export DJANGO_ALLOWED_HOSTS="*"
export DJANGO_DEBUG="1"

# 3. Seed sample data (creates the image files on the server)
python manage.py seed_cards

# 4. Run the server
python manage.py runserver 0.0.0.0:8000
```

For local development:

```bash
python manage.py migrate
python manage.py runserver
```
