CREATE USER {{ project_name|lower }};
CREATE DATABASE {{ project_name|lower }};
GRANT ALL PRIVILEGES ON DATABASE {{ project_name|lower }} TO {{ project_name|lower }};
-- On Postgres 15+, connect to the database and grant schema permissions.
-- GRANT USAGE, CREATE ON SCHEMA public TO openforms;