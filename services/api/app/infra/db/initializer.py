from sqlalchemy import inspect

from app.infra.db.base import Base
from app.infra.db.session import DatabaseManager

# Import ORM models so SQLAlchemy can register tables on metadata.
from app.infra.db import models  # noqa: F401


def _ensure_character_profile_column(sync_connection) -> None:
    inspector = inspect(sync_connection)
    if "characters" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("characters")
    }
    if "profile" in existing_columns:
        return

    # 兼容已有数据库：当前仓库还没有正式 migration 体系，这里先补一个最小加列步骤。
    sync_connection.exec_driver_sql(
        "ALTER TABLE characters ADD COLUMN profile JSON"
    )


async def initialize_database(database: DatabaseManager) -> None:
    async with database.engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        await connection.run_sync(_ensure_character_profile_column)
