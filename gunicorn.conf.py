# Gunicorn configuration file
import multiprocessing
import os

# Server socket
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
backlog = 2048

# Worker processes
workers = os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1)
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')

# Process naming
proc_name = 'web-stryker'

# SSL (uncomment for HTTPS)
# keyfile = 'path/to/keyfile'
# certfile = 'path/to/certfile'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
# ssl_version = ssl.PROTOCOL_TLS
# cert_reqs = ssl.CERT_NONE

# Debug
reload = os.getenv('GUNICORN_RELOAD', 'false').lower() == 'true'
reload_extra_files = []

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    pass

def on_reload(server):
    """Called before code is reloaded."""
    pass

def when_ready(server):
    """Called just after the server is started."""
    pass

def on_exit(server):
    """Called just before the server exits."""
    pass
