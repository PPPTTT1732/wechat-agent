import os
import ssl
from celery import Celery

# L'URL Redis Serverless (Upstash)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "wechat_agent_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['apps.worker.tasks']
)

celery_config = {
    "task_serializer": 'json',
    "accept_content": ['json'],
    "result_serializer": 'json',
    "timezone": 'UTC',
    "enable_utc": True,
    "task_track_started": True,
}

# 🔐 Configuration de sécurité spécifique pour les serveurs Serverless TLS (ex: Upstash)
if REDIS_URL.startswith("rediss://"):
    celery_config["broker_use_ssl"] = {"ssl_cert_reqs": ssl.CERT_NONE}
    celery_config["redis_backend_use_ssl"] = {"ssl_cert_reqs": ssl.CERT_NONE}

celery_app.conf.update(**celery_config)
