import logging

from django.core.mail import send_mail

from config.celery import app

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler('celery.log')
logger.addHandler(fileHandler)


@app.task(bind=True)
def send_mail_all_member():
    send_mail(
        'Subject',
        'Message',
        'fastcampus2016@gmail.com',
        [
            'arcanelux@gmail.com',
            'dev@azelf.com',
            'lucentlux@gmail.com',
            'jagermasteryi@gmail.com',
            'hanraynor@gmail.com',
            'lhy@fastcampus.co.kr',
            'hanraynor@naver.com',
        ],
        fail_silently=False,
    )
