# deploy.py
from .base import *

config_secret_deploy = json.loads(open(CONFIG_SECRET_DEPLOY_FILE).read())

# WSGI application
WSGI_APPLICATION = 'config.wsgi.deploy.application'

# AWS settings
AWS_ACCESS_KEY_ID = config_secret_deploy['aws']['access_key_id']
AWS_SECRET_ACCESS_KEY = config_secret_deploy['aws']['secret_access_key']
AWS_STORAGE_BUCKET_NAME = config_secret_deploy['aws']['s3_bucket_name']
AWS_S3_REGION_NAME = config_secret_deploy['aws']['s3_region_name']
S3_USE_SIGV4 = True
# AWS_S3_SIGNATURE_VERSION = config_secret_deploy['aws']['s3_signature_version']

# Storage settings
STATICFILES_LOCATION = 'static'
MEDIAFILES_LOCATION = 'media'
DEFAULT_FILE_STORAGE = 'config.storages.MediaStorage'
STATICFILES_STORAGE = 'config.storages.StaticStorage'

# Static URLs
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# 배포모드니까 DEBUG는 False
DEBUG = False
ALLOWED_HOSTS = config_secret_deploy['django']['allowed_hosts']

# Database
DATABASES = config_secret_deploy['django']['databases']

print('@@@@@@ DEBUG:', DEBUG)
print('@@@@@@ ALLOWED_HOSTS:', ALLOWED_HOSTS)


# 1. RDS연동 후 데이터 들어가는지 확인
#    DJANGO_SETTINGS_MODULE=config.settings.deploy설정
#    createsuperuser커맨드 실행 후 pgAdmin으로 auth_user테이블에 데이터가 들어갔는지 확인

# - Custom User model
# member app생성, AbstractUser를 상속받은 User클래스 정의, img_profile필드(ImageField) 추가
#   AUTH_USER_MODEL에 등록
# RDS에서 데이터베이스 초기화 후 migrate실행
# User를 Django admin에 등록

# - 파일 업로드 관련 설정 
# MEDIA_URL, MEDIA_ROOT설정 -> debug.py, deploy.py에 각각 따로 설정 (같은 값)
#   MEDIA_ROOT는 프로젝트폴더/.media 폴더 사용
# 이후 img_profile필드 채웠을 때 정상적으로 파일 업로드 되는지 확인


# - Nginx에서 파일서빙을 위한 설정
#   Dockerfile에서 supervisord부분 주석처리 -> 빌드
#   새 이미지로 run, 하나의 shell을 더 열기 위해 exec로 zsh실행
#   각각의 shell에서 uwsgi, nginx를 실행
#   9000번 포트에서 연결확인
#   /static/, /media/에 alias연결
#   설정 완료했으면 Dockerfile에서 supervisord부분 주석 해제, 빌드, run후 static파일 정상출력 확인