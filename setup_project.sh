#!/bin/bash

# Create project directories
mkdir -p docker mottoagents/frontend/app logs

# Create config files
cat > docker/nginx.conf << 'EOL'
user user;
worker_processes 1;
daemon off;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include mime.types;
    default_type application/octet-stream;
    sendfile on;
    keepalive_timeout 65;
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    server {
        listen 7860;
        server_name localhost;
        client_max_body_size 0;

        location / {
            include uwsgi_params;
            uwsgi_pass unix:///tmp/uwsgi.sock;
            uwsgi_read_timeout 300s;
            uwsgi_send_timeout 300s;
        }

        location /static {
            alias /app/mottoagents/frontend/app/static;
        }
    }
}
EOL

cat > docker/supervisord.conf << 'EOL'
[supervisord]
nodaemon=true
user=user
logfile=/tmp/supervisord.log
logfile_maxbytes=0

[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
autostart=true
autorestart=true

[program:uwsgi]
command=/usr/bin/uwsgi --ini /etc/uwsgi/uwsgi.ini
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
autostart=true
autorestart=true
EOL

cat > docker/uwsgi.ini << 'EOL'
[uwsgi]
socket = /tmp/uwsgi.sock
chmod-socket = 664
chown-socket = user:user
cheaper = 2
processes = 4
master = true
module = mottoagents.frontend.app:app
python-path = /home/user
uid = user
gid = user
enable-threads = true
single-interpreter = true
need-app = true
wsgi-file = /home/user/mottoagents/app.py
callable = app
EOL

# Make scripts executable
chmod +x build.sh setup_project.sh

echo "Project structure created successfully!"
ls -la docker/
