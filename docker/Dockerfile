FROM python:3.10-slim AS builder

# Set environment variables for build
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    MAKEFLAGS="-j$(nproc)"

# Install build dependencies with retry mechanism
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    for i in {1..3}; do \
        apt-get install -y --no-install-recommends --fix-missing \
        build-essential \
        gcc \
        g++ \
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        curl \
        git \
        && break || sleep 1; \
    done && \
    rm -rf /var/lib/apt/lists/*

# Create app directory and set pip config
WORKDIR /build
RUN pip config set global.index-url https://pypi.org/simple/ \
    && pip config set global.trusted-host pypi.org \
    && pip config set global.retries 3

# Install pip tools for dependency management with retry and upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip \
    for i in {1..3}; do \
        pip install --no-cache-dir -U pip setuptools wheel pip-tools && break || sleep 1; \
    done

# Copy and process requirements
COPY requirements.prod.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip-compile requirements.prod.txt --output-file requirements.locked.txt && \
    for i in {1..3}; do \
        pip install --prefix=/install -r requirements.locked.txt && break || sleep 1; \
    done

# Final stage
FROM python:3.10-slim

# Install nginx and uwsgi
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    for i in {1..3}; do \
        apt-get install -y --no-install-recommends --fix-missing \
            nginx \
            uwsgi \
            uwsgi-plugin-python3 \
            curl \
            python3-setuptools \
            python3-wheel \
            && break || sleep 1; \
    done && \
    rm -rf /var/lib/apt/lists/*

ENV LISTEN_PORT=7860 \
    USE_HTML_ROOT=/app/mottoagents/frontend/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 7860

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Create required directories with correct permissions
RUN mkdir -p /app/mottoagents/frontend/app && \
    mkdir -p /home/user/.local/bin && \
    mkdir -p /etc/supervisor/conf.d && \
    mkdir -p /etc/uwsgi && \
    chown -R 1000:1000 /app /home/user

# Enable more verbose output for package management
RUN set -x && \
    chown -R 1000:1000 \
        /app \
        /etc/nginx \
        /usr/local/lib/python3.10/site-packages \
        /usr/local/bin \
        /var/log \
        /var/run \
        /etc/supervisor/conf.d \
        /run \
        /tmp \
        /etc/uwsgi \
        /var/cache

# Set up a new user named "user" with user ID 1000
RUN set -x && \
    useradd -m -u 1000 user && \
    chown -R user:user /home/user

# Copy configuration files
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker/uwsgi.ini /etc/uwsgi/uwsgi.ini

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/home/user

# Create app directory
WORKDIR /home/user

# Copy only necessary files
COPY --chown=user:user mottoagents/ /home/user/mottoagents/
COPY --chown=user:user setup.py README.md /home/user/
COPY --chown=user:user docker/prestart.sh /app/prestart.sh
COPY --chown=user:user docker/entrypoint.sh /entrypoint.sh

# Install mottoagents with retry mechanism
RUN set -x && \
    for i in {1..3}; do \
        python setup.py install --user && break || sleep 1; \
    done && \
    chmod +x /entrypoint.sh && \
    chmod +x /app/prestart.sh

USER root
RUN set -x && \
    chown -R user:user /etc/supervisor/conf.d /etc/uwsgi /etc/nginx

USER user

# Add a healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
