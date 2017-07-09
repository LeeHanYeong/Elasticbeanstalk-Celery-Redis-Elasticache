import json
import os

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.join(ROOT_DIR, 'django_app')
CONF_DIR = os.path.join(ROOT_DIR, '.config')
CONF_DOCKER_DIR = os.path.join(CONF_DIR, 'docker')
CONF_PUBLIC_FILE = os.path.join(CONF_DIR, 'settings_public.json')

CONF_SECRET_DIR = os.path.join(ROOT_DIR, '.config_secret')
CONF_SECRET_COMMON_FILE = os.path.join(CONF_SECRET_DIR, 'settings_common.json')
CONF_SECRET_DEBUG_FILE = os.path.join(CONF_SECRET_DIR, 'settings_debug.json')
CONF_SECRET_DEPLOY_FILE = os.path.join(CONF_SECRET_DIR, 'settings_deploy.json')

# Secret config
if not os.path.exists(CONF_SECRET_DIR):
    os.makedirs(CONF_SECRET_DIR)
if not os.path.exists(CONF_SECRET_COMMON_FILE):
    open(CONF_SECRET_COMMON_FILE, 'wt').write('{}')
if not os.path.exists(CONF_SECRET_DEBUG_FILE):
    open(CONF_SECRET_DEBUG_FILE, 'wt').write('{}')
if not os.path.exists(CONF_SECRET_DEPLOY_FILE):
    open(CONF_SECRET_DEPLOY_FILE, 'wt').write('{}')

# Public config (Docker)
config_public = json.loads(open(CONF_PUBLIC_FILE).read())
config_secret_common = json.loads(open(CONF_SECRET_COMMON_FILE).read())
config_secret_debug = json.loads(open(CONF_SECRET_DEBUG_FILE).read())
config_secret_deploy = json.loads(open(CONF_SECRET_DEPLOY_FILE).read())
