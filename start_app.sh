#!/bin/sh



python manage.py makemigrations 
python manage.py migrate 

echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@admin.com', 'password1')" | python3 manage.py shell

# celery -A post_analyzer worker --loglevel=info &

python manage.py runserver 0.0.0.0:8000







