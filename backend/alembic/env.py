import os

from alembic import context
from sqlmodel import SQLModel

from app import models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import create_engine

    with create_engine(config.get_main_option("sqlalchemy.url")).connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

