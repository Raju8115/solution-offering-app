from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

# --------------------------------------------------------
# 🔧 Load environment and project setup
# --------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Load environment variables (from .env)
load_dotenv()

# Import Base and models so Alembic can autogenerate correctly
from app.database import Base
from app.models import (
    Brand, Product, Offering, Activity,
    StaffingDetail, PricingDetail, Country
)

# --------------------------------------------------------
# Alembic Config setup
# --------------------------------------------------------
config = context.config

# ✅ Override sqlalchemy.url with the one from your environment (.env)
# Example in .env:
# DATABASE_URL="mysql+pymysql://user:pass@host:4000/dbname?ssl_verify_cert=false&ssl_verify_identity=false"
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL is missing. Please set it in your .env file.")

config.set_main_option("sqlalchemy.url", database_url)

# --------------------------------------------------------
# Logging and metadata
# --------------------------------------------------------
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The metadata object from your Base (for autogenerate)
target_metadata = Base.metadata

# --------------------------------------------------------
# Offline migrations
# --------------------------------------------------------
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

# --------------------------------------------------------
# Online migrations
# --------------------------------------------------------
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

# --------------------------------------------------------
# Entry point
# --------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
