from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, text

from config import get_config
from db.tables.base import Base

config = context.config
main_config = get_config()

fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = main_config.db_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema="news",
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    def _init_schemas(connection) -> None:
        """
        We need to initialize the news schema if it doesn't
        exist already.
        :return: None
        """
        connection.execute(
            text(
                f"""
                CREATE SCHEMA IF NOT EXISTS news;
                CREATE USER news WITH PASSWORD '{main_config.db_username_password}';
                GRANT CONNECT ON DATABASE news TO news;
                SET search_path TO news;
                """
            )
        )

    db_url = main_config.db_url
    config_ini_section = config.get_section(config.config_ini_section)
    config_ini_section["sqlalchemy.url"] = db_url

    connectable = engine_from_config(
        config_ini_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema="news",
        )

        with context.begin_transaction():
            _init_schemas(connection)
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
