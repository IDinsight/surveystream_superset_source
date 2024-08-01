import os
from cachelib import RedisCache
from celery.schedules import crontab
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from superset.tasks.types import ExecutorType
from datetime import timedelta


# Configure csv and image upload folders
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = BASE_DIR + "/app/static/uploads/"
IMG_UPLOAD_FOLDER = BASE_DIR + "/app/static/uploads/"


def get_env_variable(var_name, default=None):
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        else:
            error_msg = "The environment variable {} was missing, abort...".format(
                var_name
            )
            raise EnvironmentError(error_msg)


class CeleryConfig(object):
    BROKER_URL = get_env_variable("RESULTS_BACKEND_REDIS_URL")
    CELERY_IMPORTS = (
        "superset.sql_lab",
        "superset.tasks",
        "superset.tasks.thumbnails",
    )
    CELERY_RESULT_BACKEND = get_env_variable("RESULTS_BACKEND_REDIS_URL")
    CELERYD_PREFETCH_MULTIPLIER = 10
    CELERY_ACKS_LATE = True
    CELERY_ANNOTATIONS = {
        "tasks.add": {"rate_limit": "10/s"},
        "sql_lab.get_sql_results": {"rate_limit": "100/s"},
        "email_reports.send": {
            "rate_limit": "1/s",
            "time_limit": 600,
            "soft_time_limit": 600,
            "ignore_result": True,
        },
    }
    CELERYBEAT_SCHEDULE = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=0, hour=0),
        },
    }


SCREENSHOT_LOCATE_WAIT = 100
SCREENSHOT_LOAD_WAIT = 600

MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY", "")

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": int(timedelta(days=1).total_seconds()),
    "CACHE_KEY_PREFIX": "superset_cache",
    "CACHE_REDIS_HOST": get_env_variable("REDIS_HOST"),
    "CACHE_REDIS_PORT": get_env_variable("REDIS_PORT"),
    "CACHE_REDIS_DB": 1,
}

FILTER_STATE_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": int(timedelta(days=90).total_seconds()),
    "CACHE_KEY_PREFIX": "superset_filter_state_cache",
    "CACHE_REDIS_HOST": get_env_variable("REDIS_HOST"),
    "CACHE_REDIS_PORT": get_env_variable("REDIS_PORT"),
    "CACHE_REDIS_DB": 2,
}

DATA_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": int(timedelta(hours=2).total_seconds()),
    "CACHE_KEY_PREFIX": "superset_data_cache",
    "CACHE_REDIS_HOST": get_env_variable("REDIS_HOST"),
    "CACHE_REDIS_PORT": get_env_variable("REDIS_PORT"),
    "CACHE_REDIS_DB": 3,
}

EXPLORE_FORM_DATA_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": int(timedelta(hours=2).total_seconds()),
    "CACHE_KEY_PREFIX": "superset_explore_form_data_cache",
    "CACHE_REDIS_HOST": get_env_variable("REDIS_HOST"),
    "CACHE_REDIS_PORT": get_env_variable("REDIS_PORT"),
    "CACHE_REDIS_DB": 4,
}

THUMBNAIL_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": int(timedelta(days=1).total_seconds()),
    "CACHE_KEY_PREFIX": "thumbnail_",
    "CACHE_REDIS_HOST": get_env_variable("REDIS_HOST"),
    "CACHE_REDIS_PORT": get_env_variable("REDIS_PORT"),
    "CACHE_REDIS_DB": 5,
}

SQLALCHEMY_DATABASE_URI = get_env_variable("ENV_SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = "thisISaSECRET_1234"
# SECRET_KEY = get_env_variable("FLASK_SECRET_KEY")


CELERY_CONFIG = CeleryConfig
RESULTS_BACKEND = RedisCache(
    host=get_env_variable("REDIS_HOST"),
    port=get_env_variable("REDIS_PORT"),
    key_prefix="superset_results",
)
if get_env_variable("CONFIG") == "DEVELOPMENT":
    origin_urls = ["http://localhost:8080", "http://localhost:80"]

elif get_env_variable("CONFIG") == "PRODUCTION":
    ENABLE_PROXY_FIX = True
    SUPERSET_WEBSERVER_PROTOCOL = "https"

    WEBDRIVER_BASEURL = "http://superset:8088/"
    WEBDRIVER_BASEURL_USER_FRIENDLY = "https://superset.surveystream.idinsight.io/"

    SESSION_COOKIE_DOMAIN = ".superset.surveystream.idinsight.io"
    SUPERSET_WEBSERVER_DOMAINS = [
        "superset.surveystream.idinsight.io",
        "shard0.superset.surveystream.idinsight.io",
        "shard1.superset.surveystream.idinsight.io",
        "shard2.superset.surveystream.idinsight.io",
        "shard3.superset.surveystream.idinsight.io",
    ]

    ENABLE_CORS = True
    origin_urls = [
        "https://superset.surveystream.idinsight.io",
        "https://airflow.surveystream.idinsight.io/",
    ]

    CORS_OPTIONS = {
        "supports_credentials": True,
        "allow_headers": "*",
        "expose_headers": "*",
        "origins": origin_urls,
    }

    sentry_sdk.init(
        dsn="https://829a8af8dcdf3abfc43cc21270bb6376@o564222.ingest.sentry.io/4505882860257280",
        max_breadcrumbs=50,
        integrations=[FlaskIntegration(), SqlalchemyIntegration()],
        profiles_sample_rate=1.0,
        traces_sample_rate=1.0,
    )

    TALISMAN_CONFIG = {
        "content_security_policy": {
            "default-src": ["'self'", "*.superset.surveystream.idinsight.io"],
            "img-src": ["https:", "blob:", "data:"],
            "worker-src": ["'self'", "blob:"],
            "connect-src": [
                "'self'",
                "https://api.mapbox.com",
                "https://events.mapbox.com",
                "*.superset.surveystream.idinsight.io",
            ],
            "object-src": "'none'",
            "style-src": [
                "'self'",
                "'unsafe-inline'",
            ],
            "script-src": [
                "'self'",
                "'strict-dynamic'",
                "'unsafe-eval'",
                "'unsafe-inline'",
            ],
        },
        "content_security_policy_nonce_in": ["script-src"],
        "force_https": False,
    }
else:
    WEBDRIVER_BASEURL = "http://superset:8088/"
    WEBDRIVER_BASEURL_USER_FRIENDLY = "http://localhost:80/"


# Update query rows limit - Default value was 50,000. This can be changed further, if needed
ROW_LIMIT = 1000000

# Details for geneerating screenshots for
# THUMBNAIL_SELENIUM_USER = get_env_variable("INIT_SUPERSET_USER")
# THUMBNAIL_EXECUTE_AS = [ExecutorType.SELENIUM]
# ALERT_REPORTS_EXECUTE_AS = [ExecutorType.SELENIUM]

FEATURE_FLAGS = {
    "ROW_LEVEL_SECURITY": True,
    "ALERT_REPORTS": True,
    "THUMBNAILS": False,
    "THUMBNAILS_SQLA_LISTENERS": False,
    "DASHBOARD_RBAC": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DRILL_TO_DETAIL": True,
    "AUTH_ROLE_PUBLIC": "Public",
    "ENABLE_JAVASCRIPT_CONTROLS": True,
    "ALERT_REPORTS_NOTIFICATION_DRY_RUN": False,
    "HORIZONTAL_FILTER_BAR": True,
    "TAGGING_SYSTEM": True,
    # "DYNAMIC_PLUGINS": True # creating issues in loading dashboard create
}

EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": "IDinsight Theme",
        "description": "Theme with IDinsight colors",
        "label": "IDinsight visualization colors",
        "colors": [
            "#156182",
            "#0D82BB",
            "#7A8A91",
            "#0D82BB",
            "#7CB2D7",
            "#7A8A91",
            "#FFFFFF",
        ],
    }
]

# SMTP server configuration for sending alerts and reports to users via emails
EMAIL_NOTIFICATIONS = True
SMTP_HOST = "smtp.sendgrid.net"
SMTP_STARTTLS = True
SMTP_SSL = False
SMTP_USER = "apikey"
SMTP_PORT = 587
SMTP_PASSWORD = get_env_variable("SMTP_PASSWORD")
SMTP_MAIL_FROM = "surveystream@idinsight.org"

SUPERSET_DASHBOARD_POSITION_DATA_LIMIT = 1000000  # 65535 - default for MySQL db

PUBLIC_ROLE_LIKE = "Gamma"
