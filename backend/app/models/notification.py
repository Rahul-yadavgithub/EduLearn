from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Notification(BaseModel):
    notification_id: str
    user_id: str
    message: str
    type: str  # doubt_answered | teacher_approved | teacher_revoked
    is_read: bool = False
    created_at: datetime
    related_id: Optional[str] = None
