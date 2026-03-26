from datetime import datetime

from pydantic import BaseModel


class PlanItem(BaseModel):
    id: str
    title: str
    start_at: datetime
    end_at: datetime
    priority: int = 1

