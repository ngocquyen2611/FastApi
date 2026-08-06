import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# =========================================================================
# 1. FIX PATH: Thêm thư mục gốc dự án vào sys.path
# =========================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# =========================================================================
# 2. IMPORT CÁC MODULE TỪ DỰ ÁN FASTAPI
# =========================================================================
from src.core.config import settings
from src.core.database import Base

# Import model để Alembic nhận diện bảng khi autogenerate
import src.models.base  # noqa: F401

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# =========================================================================
# 3. CẤU HÌNH DATABASE URL VÀ METADATA
# =========================================================================
# Ép Alembic chuyển +asyncpg thành +psycopg2 vì Alembic Migration chạy Sync
db_url = settings.database_url.replace("+asyncpg", "+psycopg2")
config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section, {})
    # Đảm bảo dùng db_url chuẩn sync
    configuration["sqlalchemy.url"] = db_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()