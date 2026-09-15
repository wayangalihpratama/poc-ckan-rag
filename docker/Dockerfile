FROM --platform=linux/amd64 ckan/ckan-base:2.10.4

USER root

# Install system dependencies
RUN apk update && \
    apk add --no-cache \
        curl \
        git \
        bash \
        gcc \
        musl-dev \
        postgresql-client

# Install testing dependencies
RUN pip install --no-cache-dir --ignore-installed pytest pytest-cov

# Set working directory for extensions
WORKDIR /srv/app

# Copy custom entrypoint script
COPY docker/entrypoint.sh /srv/app/entrypoint.sh
RUN chmod +x /srv/app/entrypoint.sh

ENTRYPOINT ["/srv/app/entrypoint.sh"]
CMD ["ckan", "run", "-H", "0.0.0.0", "-p", "5000"]
