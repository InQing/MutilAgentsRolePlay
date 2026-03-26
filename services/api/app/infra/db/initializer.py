from app.infra.db.base import Base
from app.infra.db.session import DatabaseManager

# Import ORM models so SQLAlchemy can register tables on metadata.
from app.infra.db import models  # noqa: F401


async def initialize_database(database: DatabaseManager) -> None:
    async with database.engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
