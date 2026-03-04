from logging import getLogger
from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import create_engine, engine_from_config, pool, text

from common.database.postgres.models import BaseModel
from common.utils.env import load_environment_variables

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = BaseModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

logger = getLogger("alembic.env")


def get_db_url():
    """Get the database URL using the environment variables.

    The environment variables used are:

    - DB_HOST: the hostname of the database server
    - DB_PORT: the port number of the database server (default: 3306)
    - DB_USER: the username to use when connecting to the database
    - DB_PASSWORD: the password to use when connecting to the database
    - DB_DATABASE: the name of the database to connect to

    Returns:
        str: the database URL
    """
    load_environment_variables()
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")

    return (
        f"postgresql+psycopg2://{POSTGRES_USER}"
        f":{POSTGRES_PASSWORD}@{POSTGRES_HOST}:"
        f"{POSTGRES_PORT}/{POSTGRES_DATABASE}"
    )


def create_database(url):
    """Create a PostgreSQL database.

    Args:
        url (str): The URL of the database, including the database name.

    Returns:
        None
    """
    database = url.rsplit("/", 1)[-1]
    url = url.replace(database, "postgres")

    admin_engine = create_engine(url=url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :database"),
            {"database": database},
        ).scalar()

        if exists is None:
            conn.execute(text(f"CREATE DATABASE {database}"))
            logger.info(f"Database {database} created")
        else:
            logger.info(f"Database {database} already exists")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    POSTGRES_URL = get_db_url()
    create_database(POSTGRES_URL)
    config.set_main_option("sqlalchemy.url", POSTGRES_URL)

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    POSTGRES_URL = get_db_url()
    create_database(POSTGRES_URL)
    config.set_main_option("sqlalchemy.url", POSTGRES_URL)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
