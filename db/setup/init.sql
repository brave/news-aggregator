-- This file contains sql commands that must run prior
-- to migrations. The most common one is schema migration
-- because schemas have their own alembic migration table
-- and alembic expects the schema to exist when it tries
-- to initialize its migration table.


CREATE SCHEMA IF NOT EXISTS news;
