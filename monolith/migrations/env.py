from alembic import context
from sqlalchemy import create_engine
from app.infrastructure.database import sqlalchemy_url

engine = create_engine(sqlalchemy_url())
with engine.connect() as connection:
    context.configure(connection=connection)
    with context.begin_transaction():
        context.run_migrations()
