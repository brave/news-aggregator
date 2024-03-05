-- This file contains sql commands that must run prior
-- to migrations. The most common one is schema migration
-- because schemas have their own alembic migration table
-- and alembic expects the schema to exist when it tries
-- to initialize its migration table.
--
-- This file is used by devs for initializing their db, calling it
-- directly with psql: `psql -U spend -f spend/db/setup/init.sql spend`
-- and is also used as an "init_sql_file" passed to `TestDBConfig`
-- to handle test database setup in integration tests.
-- When integration db setup happens, we can't "batch" execute the
-- whole file like we can with psql. Instead we have to exec each
-- transaction separately. To support both use-cases, each command
-- in this file should be separated by a line containing the
-- comment `-- command`. Test db-setup will split the file using
-- this comment and exec each line separately. See `setup_test_db`
-- for details

CREATE SCHEMA IF NOT EXISTS news;
