#!/bin/bash

docker pull postgres

docker run --name postgres-db \
  -e POSTGRES_PASSWORD=TopSecret \
  -e POSTGRES_USER=padmin \
  -e POSTGRES_DB=testdb \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql \
  -d postgres

# psql -U padmin
# CREATE USER padmin SUPERUSER;
# ALTER ROLE padmin WITH PASSWORD 'TopSecret';
# CREATE DATABASE testdb OWNER padmin;


docker pull crystaldba/postgres-mcp

docker run -p 8000:8000 \                                                                                                                        ✔ │ 21s │ 15:13:16 
  -e DATABASE_URI=postgresql://padmin:TopSecret@localhost:5432/testdb \
  crystaldba/postgres-mcp --access-mode=unrestricted --transport=sse