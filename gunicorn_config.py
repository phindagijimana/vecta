import os

bind = "0.0.0.0:8081"
workers = 1            # GPU-safe
worker_class = "sync"
worker_connections = 10
timeout = 300
keepalive = 2
preload_app = False    # do NOT import app before forking

# Logs
service_log_dir = os.environ.get("SERVICE_LOG_DIR", "logs")
os.makedirs(service_log_dir, exist_ok=True)
accesslog = os.path.join(service_log_dir, "access.log")
errorlog  = os.path.join(service_log_dir, "error.log")
loglevel  = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

proc_name = "vectaai_service"
worker_tmp_dir = "/dev/shm"
