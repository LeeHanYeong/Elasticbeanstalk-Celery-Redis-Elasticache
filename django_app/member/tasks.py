import logging

import time
from django.core.mail import send_mail

from config.celery import app

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler('celery.log')
logger.addHandler(fileHandler)


@app.task(bind=True, default_retry_delay=120)
def send_mail_task(self, title, message, recipient_list=None):
    time.sleep(20)
    if not recipient_list:
        recipient_list = [
            'arcanelux@gmail.com',
            'dev@azelf.com',
            'lucentlux@gmail.com',
            'jagermasteryi@gmail.com',
            'hanraynor@gmail.com',
            'lhy@fastcampus.co.kr',
            'hanraynor@naver.com',
        ]
    try:
        return send_mail(
            title,
            message,
            'fastcampus2016@gmail.com',
            recipient_list,
        )
    except Exception as exc:
        raise self.retry(exc=exc)
