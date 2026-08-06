from typing import Optional, Literal, List
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel, Field

# Thứ tự vòng đời DailySession. main.py chỉ ĐƯỢC PHÉP tiến tới, không cho lùi,
# và state không lộ ra thành 1 menu tay — nó tự đổi theo hành động người dùng
# thực hiện (mở calendar, ghi mood, thêm task, hoàn thành task, thoát ngày).
SESSION_STATE_FLOW = ["Created", "Planning", "Active", "Reviewing", "Closed"]


class Task(BaseModel):
    """Đơn vị hành động người dùng cần làm.

    v0: chỉ những field tối thiểu để lọc theo mood và đánh dấu hoàn thành.
    Không có deadline/estimated_duration — những field đó thuộc FlexibleSchedule
    (v3, khi có ghi ngược vào Google Calendar), chưa mở ở v0.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    mood_affinity: Literal["High", "Neutral", "Low"]
    status: Literal["pending", "done"] = "pending"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Session(BaseModel):
    """DailySession — một chu kỳ làm việc trong ngày.

    `state` có default "Created" để tạo mới không cần truyền tay.
    `mood` optional vì mood chỉ được ghi nhận khi người dùng chủ động chọn
    ở Start of Day, không bắt buộc phải có ngay khi session được tạo.
    """
    date: str
    state: Literal["Created", "Planning", "Active", "Reviewing", "Closed"] = "Created"
    mood: Optional[Literal["High", "Neutral", "Low"]] = None
    task_ids: List[str] = []