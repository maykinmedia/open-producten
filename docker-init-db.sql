CREATE USER open_producten;
CREATE DATABASE open_producten;
GRANT ALL PRIVILEGES ON DATABASE open_producten TO open_producten;
-- On Postgres 15+, connect to the database and grant schema permissions.
-- GRANT USAGE, CREATE ON SCHEMA public TO openforms;
