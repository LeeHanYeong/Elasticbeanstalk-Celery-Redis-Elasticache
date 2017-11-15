FROM        azelf/eb-celery
MAINTAINER  dev@azelf.com

# DJANGO_SETTINGS_MODULE설정
WORKDIR     /srv/app/django_app
CMD         supervisord -n
EXPOSE      80 8000