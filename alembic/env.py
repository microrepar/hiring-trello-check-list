from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool

from alembic import context
from src.external.persistence.sqlalchemyorm.model.base import Base
from config import Config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    config.set_main_option( "sqlalchemy.url" , Config.DATABASE_URL)
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# recovers the schema if it is missing in the table metadata
schema_name = None
for table_name in target_metadata.tables.keys():
    schema_name = target_metadata.tables.get(table_name, target_metadata).schema
    if schema_name is not None:
        break


def include_name(name, type_, parent_names):
    if type_ == "schema":
        # this **will* include the default schema
        return name in [None, schema_name]
    else:
        return True
    

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        if schema_name:
            context.configure(
                connection=connection, 
                target_metadata=target_metadata,
                version_table_schema=schema_name,
                compare_type=True,
                include_schemas=True,
                include_name=include_name,
            )
            connection.execute(f'CREATE SCHEMA IF NOT EXISTS {schema_name}')
        else:
            context.configure(
                connection=connection, 
                target_metadata=target_metadata,
                compare_type=True,
                include_schemas=True,
                include_name=include_name,
            )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
