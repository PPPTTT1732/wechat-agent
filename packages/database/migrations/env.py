import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Permet à Alembic de trouver nos paquets locaux
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# 🚨 IMPORTANT : Importation de nos modèles pour générer les migrations automatiques
from packages.database.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# On indique à Alembic de surveiller nos tables
target_metadata = Base.metadata

def get_url():
    # En production, on lit l'URL Neon depuis l'environnement
    return os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
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
