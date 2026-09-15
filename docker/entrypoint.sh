#!/bin/bash
set -e

echo "=== Starting CKAN Akvo RAG Container Setup ==="

# Wait for PostgreSQL
echo "Waiting for PostgreSQL database at ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}..."
until pg_isready -h "${POSTGRES_HOST:-db}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-ckan_default}"; do
  echo "PostgreSQL is unavailable - sleeping 2s..."
  sleep 2
done
echo "PostgreSQL is up and ready."

# Wait for Solr
echo "Waiting for Solr at ${CKAN_SOLR_URL:-http://solr:8983/solr/ckan}..."
until curl -sf "${CKAN_SOLR_URL:-http://solr:8983/solr/ckan}/admin/ping?wt=json" | grep -q '"status":"OK"'; do
  echo "Solr core is unavailable - sleeping 2s..."
  sleep 2
done
echo "Solr core is up and ready."

# Ensure ckan.ini is copied
if [ -f "/srv/app/src_extensions/ckanext-akvorag/docker/ckan.ini" ]; then
    echo "Applying custom ckan.ini configuration..."
    cp /srv/app/src_extensions/ckanext-akvorag/docker/ckan.ini /srv/app/ckan.ini
fi

# Install ckanext-akvorag in editable mode if mounted
if [ -d "/srv/app/src_extensions/ckanext-akvorag" ]; then
    echo "Installing ckanext-akvorag in editable development mode..."
    pip install -e /srv/app/src_extensions/ckanext-akvorag
fi

# Initialize CKAN DB if not already initialized
echo "Checking CKAN Database tables..."
ckan -c /srv/app/ckan.ini db init || true

echo "CKAN initialization complete. Starting server..."
exec "$@"
