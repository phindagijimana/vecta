import multiprocessing
import os

# Server socket
bind = "{}:{}".format(os.environ.get('SERVICE_HOST', '0.0.0.0'), os.environ.get('SERVICE_PORT', '8081'))
backlog = 2048

# Worker processes
workers = 1  # Single worker for GPU model
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 10
max_requests = 1000
max_requests_jitter = 50

# Restart workers after this many requests (with some jitter)
preload_app = False

# Logging
#accesslog = f"{os.environ.get('SERVICE_LOG_DIR', '.')}/gunicorn_access.log"
#errorlog = f"{os.environ.get('SERVICE_LOG_DIR', '.')}/gunicorn_error.log"
accesslog = "{}/gunicorn_access.log".format(os.environ.get('SERVICE_LOG_DIR', '.'))
errorlog = "{}/gunicorn_error.log".format(os.environ.get('SERVICE_LOG_DIR', '.'))

loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "vectaai_service"

# Server mechanics
daemon = False
#pidfile = f"{os.environ.get('APP_HOME', '.')}/gunicorn.pid"
pidfile = "{}/gunicorn.pid".format(os.environ.get('APP_HOME', '.'))
tmp_upload_dir = None

def on_starting(server):
    server.log.info("Vecta AI service starting with Gunicorn")

def when_ready(server):
    server.log.info("Vecta AI service ready with optimized prompting")

def on_exit(server):
    server.log.info("Vecta AI service shutting down")
