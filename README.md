# qr_ticket_system

Django app for generating QR tickets and scanning them.

## Quick local setup

1. Create virtualenv, install requirements:
'''
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
'''

2. Copy `.env.example` values to `.env` (or set env vars).
Required env vars for production:
- `SECRET_KEY`
- `DEBUG` (optional)
- `DATABASE_URL` (Heroku sets this automatically)

3. Run migrations and create superuser:
'''
python manage.py migrate
python manage.py createsuperuser
'''

4. Run server:
'''
python manage.py runserver
'''

## Heroku notes

- Files saved to `media/` are ephemeral on Heroku. For persistent storage, configure S3 (not included here).
- Heroku config vars should be used for `SECRET_KEY` and `DATABASE_URL`.

## Scanner user

Create a scanner user via Django admin, put them in group `Scanner` or set `is_staff=True`. Scanner and Admin can sign in at `/admin/` (or use /accounts/login/ if you add dj-auth later).

