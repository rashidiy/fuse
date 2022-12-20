import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import Celery
from decouple import config

# set the default Django settings module for the 'celery' program.
# this is also used in manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')

app = Celery('cfehome')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


# We used CELERY_BROKER_URL in settings.py instead of:
# app.conf.broker_url = ''

# We used CELERY_BEAT_SCHEDULER in settings.py instead of:
# app.conf.beat_scheduler = ''django_celery_beat.schedulers.DatabaseScheduler'

@app.task
def send_text_to_mail(to_email, text, subject: str = None, type_: str = 'plain'):
    msg = MIMEMultipart()
    app_password = 'ogqbxmufcmwjjhzw'
    my_email = 'bubbless7456@gmail.com'
    msg['Subject'] = subject
    msg['From'] = my_email
    msg['To'] = to_email
    msg.attach(MIMEText(text, type_))
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(my_email, app_password)
        smtp.send_message(msg)
