"""Alembic migration runtime configuration.

迁移使用 PERSON_UP_DATABASE_URL 指向目标数据库；不要在日志或异常中输出完整 DSN。
"""

from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def database_url() -> str:
    """读取迁移数据库 URL；缺失时用稳定错误提示终止迁移。"""
    url = os.environ.get("PERSON_UP_DATABASE_URL")
    if not url:
        raise RuntimeError("PERSON_UP_DATABASE_URL is required to run migrations.")
    return url


config.set_main_option("sqlalchemy.url", database_url())


def run_migrations_offline() -> None:
    """生成离线迁移 SQL，不建立数据库连接。"""
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
    """连接目标数据库并执行在线迁移。"""
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
