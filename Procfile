web: python manage.py collectstatic --noinput && python manage.py migrate --noinput && gunicorn Projet_Parfeu.wsgi --bind 0.0.0.0:$PORT
