from __future__ import annotations

import datetime
import uuid
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

MoodLevel = Literal["High", "Neutral", "Low"]
TaskStatus = Literal["pending", "done"]
SessionState = Literal["Created", "Planning", "Active", "Reviewing", "Closed"]

# Thứ tự vòng đời hợp lệ của DailySession (04_domain_model.md mục 4).
# Dùng để đảm bảo state chỉ tiến, không bao giờ lùi hoặc nhảy cóc ngược.
STATE_ORDER: List[SessionState] = ["Created", "Planning", "Active", "Reviewing", "Closed"]


class Task(BaseModel):
    """Task là Global entity — KHÔNG gắn cứng vào 1 DailySession cụ thể.

    `Task.scheduled_date` là single source of truth cho việc task thuộc về
    ngày nào (Today / Overdue / Unscheduled) — DailySession không lưu danh
    sách Task nào của riêng nó (xem thêm ghi chú trong Session bên dưới).

    `created_at`/`completed_at` luôn lưu dưới dạng UTC-aware datetime — KHÔNG
    tự convert sang giờ local ở tầng model. Muốn biết task thuộc "ngày nào"
    theo giờ người dùng, dùng `src.timezone.to_app_date()` ở tầng gọi (main.py),
    không so sánh trực tiếp phần .date() của timestamp UTC.
    """

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    title: str
    mood_affinity: MoodLevel
    status: TaskStatus = "pending"
    scheduled_date: Optional[datetime.date] = None
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    completed_at: Optional[datetime.datetime] = None

    def mark_done(self) -> None:
        """Complete: giữ nguyên dữ liệu, chỉ đổi status + ghi completed_at để tracking.
        Tách biệt hẳn với xóa (Delete) — hai hành động mang ý nghĩa dữ liệu khác nhau.
        """
        self.status = "done"
        self.completed_at = datetime.datetime.now(datetime.timezone.utc)


class Session(BaseModel):
    """DailySession — một chu kỳ làm việc trong ngày (04_domain_model.md mục 4).

    KHÔNG lưu danh sách Task (không có field task_ids). "Task nào thuộc về
    ngày nào" là câu hỏi chỉ Task mới trả lời được (qua scheduled_date /
    completed_at) — Session không nhân đôi quan hệ đó để tránh 2 nguồn sự
    thật lệch nhau (VD: task Overdue được hoàn thành hôm nay không có nghĩa
    nó "thuộc về" session hôm nay).

    `state` không được set thủ công qua menu UI. Nó chỉ tự động tiến lên
    (xem `advance_to`) khi người dùng thực hiện đúng hành động tương ứng —
    mô phỏng chuỗi Start of Day -> During Day -> End of Day trong
    03_workflow.md, không phải một tính năng "chuyển state" độc lập.
    """

    date: str
    state: SessionState = "Created"
    mood: Optional[MoodLevel] = None

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

    def force_reopen(self, target: SessionState = "Active") -> None:
        """CHỈ dùng khi test tay v0 — ép state lùi lại để tiếp tục thao tác trên
        một phiên đã lỡ tay đóng (Closed). Cố tình đặt tên và tách riêng khỏi
        advance_to() để không ai nhầm đây là cách "chuyển state" bình thường —
        nguyên tắc chỉ-tiến vẫn áp dụng cho mọi luồng vận hành thật.
        """
        self.state = target