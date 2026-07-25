ARG PYTHON_VERSION=3.8.12
ARG PIP_VERSION=21.3.1

FROM python:${PYTHON_VERSION}-slim-bullseye AS base
ARG PIP_VERSION
ENV PIP_VERSION=${PIP_VERSION}
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
RUN set -eu; \
    \
# Install tzdata for localtime settings
# and tini to act as our simple init
    apt-get update -y \
    && apt-get install -y --no-install-recommends \
        tzdata \
        tini \
        libzbar-dev \
        g++ \
        sqlite3 \
        curl \
# Install mysqlclient and gcc libs
        default-libmysqlclient-dev \
        gcc \
# Cleanup
    && rm -rf /var/lib/apt/lists/*
WORKDIR /wheels
EXPOSE 8080
# Using tini as PID 1 and kernel signals handler
ENTRYPOINT [ "/usr/bin/tini", "--" ]

FROM base AS pip-build
COPY requirements.txt .
RUN set -eu; \
    \
# Install pip
    python3 -m pip install \
        --upgrade \
        "pip>=${PIP_VERSION}" \
# Install wheel for deps with reduce size and faster downloads
    && python3 -m pip install \
        --upgrade \
        wheel \
# Install application python requirements
    && python3 -m pip wheel \
        --requirement requirements.txt

FROM base AS builder
COPY --from=pip-build /wheels /wheels
WORKDIR /app
RUN set -eu; \
    \
    pip install \
        --upgrade \
        "pip>=${PIP_VERSION}" \
    && pip install \
        --pre \
        --no-cache-dir \
        --no-index \
        --requirement /wheels/requirements.txt \
        --find-links /wheels \
    && rm -rf /wheels
ENV PYTHONPATH=/app

FROM builder AS development
## Run as non-root user
# RUN useradd dev -m && chown -R dev .
# ENV PATH "/home/dev/.local/bin:$PATH"
# USER dev
# # Copy source code to container
# COPY --chown=dev:dev . .
## Run as root
# Copy source code to container
COPY . .
# Use django WSGI for development environment
CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8080" ]

FROM builder AS production
ENV ENVIRONMENT=production
RUN python3 -m pip install --no-cache-dir gunicorn==20.1.0

RUN chown 1000:1000 /app
# Using rootless user for better security
USER 1000:1000
# Copy source code to container
COPY --chown=1000:1000 . .
# Use gunicorn WSGI for production environment
# using ghthread - faster for now
CMD [ "gunicorn", "--bind=0.0.0.0:8080", "--worker-tmp-dir=/dev/shm", "--log-file=-", "--preload", "--workers=3", "--threads=5", "--worker-class=gthread", "--max-requests=1000", "registry.wsgi:application" ]


# Metadata
# Runtime distribution variables for labels
ARG BUILD_DATE
ARG VCS_COMMIT_SHA
ARG VCS_URL
LABEL org.opencontainers.image.created=${BUILD_DATE} \
      org.opencontainers.image.revision=${VCS_COMMIT_SHA} \
      org.opencontainers.image.source=${VCS_URL}