-- Create datastore database
CREATE DATABASE datastore_default OWNER ckan_default;

-- Create datastore read-only user
CREATE USER datastore_default WITH PASSWORD 'datastore_password';
GRANT CONNECT ON DATABASE datastore_default TO datastore_default;
