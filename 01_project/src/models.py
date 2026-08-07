from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

MoodLevel = Literal["High", "Neutral", "Low"]
TaskStatus = Literal["pending", "done"]
SessionState = Literal["Created", "Planning", "Active", "Reviewing", "Closed"]

# Thứ tự vòng đời hợp lệ của DailySession (04_domain_model.md mục 4).
# Dùng để đảm bảo state chỉ tiến, không bao giờ lùi hoặc nhảy cóc ngược.
STATE_ORDER: List[SessionState] = ["Created", "Planning", "Active", "Reviewing", "Closed"]


class Task(BaseModel):
    """Đơn vị hành động người dùng cần thực hiện trong ngày (04_domain_model.md mục 7)."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    title: str
    mood_affinity: MoodLevel
    status: TaskStatus = "pending"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Session(BaseModel):
    """DailySession — một chu kỳ làm việc trong ngày (04_domain_model.md mục 4).

    QUAN TRỌNG: `state` không được set thủ công qua menu UI. Nó chỉ tự động tiến lên
    (xem `advance_to`) khi người dùng thực hiện đúng hành động tương ứng — mô phỏng
    chuỗi Start of Day -> During Day -> End of Day trong 03_workflow.md, không phải
    một tính năng "chuyển state" độc lập.
    """

    date: str
    state: SessionState = "Created"
    mood: Optional[MoodLevel] = None
    task_ids: List[str] = Field(default_factory=list)

    def advance_to(self, target: SessionState) -> bool:
        """Tiến state tới `target` nếu target đứng sau state hiện tại trong vòng đời.
        Không làm gì nếu target ở cùng vị trí hoặc phía trước (idempotent, an toàn khi gọi lặp).
        Trả về True nếu state thực sự thay đổi.
        """
        current_idx = STATE_ORDER.index(self.state)
        target_idx = STATE_ORDER.index(target)
        if target_idx > current_idx:
            self.state = target
            return True
        return False