from __future__ import annotations

import datetime
import uuid
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

MoodLevel = Literal["High", "Neutral", "Low"]
TaskStatus = Literal["pending", "done", "paused"]
SessionState = Literal["Created", "Planning", "Active", "Reviewing", "Closed"]

# Thứ tự vòng đời hợp lệ của DailySession (04_domain_model.md mục 4).
STATE_ORDER: List[SessionState] = ["Created", "Planning", "Active", "Reviewing", "Closed"]

# Điểm cộng mỗi FlexibleSchedule hoàn thành — CỐ ĐỊNH (mặc định đã chọn, xem
# 00_v0_scope.md mục 6/v1). Đổi giá trị này là đủ nếu sau này muốn cân chỉnh,
# không cần sửa logic compute_score().
POINTS_PER_SCHEDULE = 1

# Số ngày không có FlexibleSchedule nào được complete trước khi Task tự
# chuyển sang "paused" (mặc định đã chọn — xem 00_v0_scope.md mục 6/v1).
PAUSE_THRESHOLD_DAYS = 14


class Task(BaseModel):
    """Task là Global entity — KHÔNG gắn cứng vào 1 DailySession cụ thể.

    `Task.scheduled_date` vẫn giữ nguyên vai trò v0 (Today/Overdue/Unscheduled
    cho việc quản lý việc vặt đơn giản, không cần track score/streak). Đây là
    field TÁCH BIỆT với hệ FlexibleSchedule bên dưới — 1 Task có thể chỉ dùng
    scheduled_date (Task-to-do đơn giản), hoặc dùng thêm FlexibleSchedule nếu
    muốn track score/streak (thường đi cùng Task-goal-directed, nhưng không
    bắt buộc — 1 Task-to-do thường vẫn có thể có FlexibleSchedule).

    `goal_id` có giá trị -> Task-goal-directed (checkpoint của 1 Goal).
    `goal_id = None` -> Task-to-do thuần. Đây là quan hệ TẬP CON, không phải
    2 loại tách biệt — nên chỉ cần 1 field Optional, không tách 2 model.

    `created_at`/`completed_at` luôn lưu dưới dạng UTC-aware datetime — KHÔNG
    tự convert sang giờ local ở tầng model. Dùng `src.timezone.to_app_date()`
    ở tầng gọi khi cần biết "ngày nào" theo giờ người dùng.
    """

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    title: str
    mood_affinity: MoodLevel
    status: TaskStatus = "pending"
    goal_id: Optional[str] = None
    scheduled_date: Optional[datetime.date] = None
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    completed_at: Optional[datetime.datetime] = None

    def mark_done(self) -> None:
        """DONE TASK: hành động THỦ CÔNG duy nhất để đóng Task. Hoàn toàn tách
        biệt khỏi score/streak — dù score cao bao nhiêu cũng không tự động
        done. Tách biệt hẳn với xóa (Delete) — hai hành động khác ý nghĩa dữ liệu.
        """
        self.status = "done"
        self.completed_at = datetime.datetime.now(datetime.timezone.utc)

    def pause(self) -> None:
        """Tự động gọi khi Task không hoạt động quá PAUSE_THRESHOLD_DAYS —
        xem check_stale_tasks(). Không xóa Task, chỉ đổi status."""
        self.status = "paused"

    def resume(self) -> None:
        """Resume: paused -> pending. Ý định là luôn đi kèm tạo FlexibleSchedule
        mới ngay sau đó ở tầng gọi (main.py) — "quay lại" luôn kèm 1 cam kết cụ thể."""
        self.status = "pending"


class Goal(BaseModel):
    """Goal — đại diện cho việc tracking progress, KHÔNG phải bản thân công việc.
    Bao gồm nhiều Task-goal-directed (Task có goal_id trỏ về Goal này) đóng
    vai trò checkpoint. Progress của Goal là GIÁ TRỊ DERIVED (xem compute_goal_progress),
    không lưu field riêng — tránh 2 nguồn sự thật.
    """

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    title: str
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )


class FlexibleSchedule(BaseModel):
    """FlexibleSchedule — khung giờ dự kiến thực hiện 1 Task, quản lý HOÀN TOÀN
    nội bộ trong app. KHÔNG phải Google Calendar event (xem 00_v0_scope.md
    mục 6 — lý do tách bạch khỏi FixedSchedule).

    Mô hình TUẦN TỰ (attempt log): tại 1 thời điểm, 1 Task chỉ nên có tối đa
    1 FlexibleSchedule đang "chờ" (completed=False) — xem active_schedule().

    completed_at tách biệt hoàn toàn với Task.completed_at (2 field khác
    entity, khác ý nghĩa: đây là lúc điểm danh 1 buổi, không phải lúc DONE TASK).
    """

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    task_id: str
    scheduled_start: datetime.datetime
    scheduled_end: datetime.datetime
    completed: bool = False
    completed_at: Optional[datetime.datetime] = None
    dismissed: bool = False

    def mark_completed(self) -> None:
        """Điểm danh buổi này. Score được tính DERIVED ở compute_score() —
        hàm này KHÔNG cộng điểm trực tiếp, tránh double-count khi load/save lặp lại."""
        self.completed = True
        self.completed_at = datetime.datetime.now(datetime.timezone.utc)

    def mark_dismissed(self) -> None:
        """Người dùng đã thấy cảnh báo miss và chọn 'Bỏ qua' (không dời lịch).
        Loại buổi này khỏi missed_schedules() vĩnh viễn — tránh cảnh báo dội
        lại vô hạn mỗi lần mở app. Buổi vẫn giữ nguyên completed=False trong
        lịch sử (không giả vờ là đã hoàn thành)."""
        self.dismissed = True


class Session(BaseModel):
    """DailySession — một chu kỳ làm việc trong ngày (04_domain_model.md mục 4).

    KHÔNG lưu danh sách Task (không có field task_ids) — tránh 2 nguồn sự
    thật lệch nhau.

    `state` không được set thủ công qua menu UI, chỉ tự động tiến lên (xem
    `advance_to`) theo hành động tương ứng.
    """

    date: str
    state: SessionState = "Created"
    mood: Optional[MoodLevel] = None

    def advance_to(self, target: SessionState) -> bool:
        current_idx = STATE_ORDER.index(self.state)
        target_idx = STATE_ORDER.index(target)
        if target_idx > current_idx:
            self.state = target
            return True
        return False

    def force_reopen(self, target: SessionState = "Active") -> None:
        """CHỈ dùng khi test tay — ép state lùi lại. Tách riêng khỏi advance_to()
        để không nhầm đây là cách chuyển state hợp lệ trong vận hành thật."""
        self.state = target


# ==========================================
# HÀM DERIVED — score/streak/warning/pause
# KHÔNG lưu field cộng dồn ở đâu cả. Mọi giá trị tính lại từ dữ liệu gốc
# (FlexibleSchedule) mỗi lần cần dùng — loại bỏ hẳn khả năng double-count
# khi load/save lặp lại, và UNCOMPLETE (nếu có sau này) không cần rollback gì.
# ==========================================

def compute_score(task_id: str, schedules: List[FlexibleSchedule]) -> int:
    """Task.score — tổng điểm từ mọi FlexibleSchedule đã completed thuộc Task này.
    Không có trần, không quy đổi phần trăm (xem thảo luận Progress/Score trong scope)."""
    return sum(POINTS_PER_SCHEDULE for s in schedules if s.task_id == task_id and s.completed)


def compute_streak(
    task_id: str,
    schedules: List[FlexibleSchedule],
    now: Optional[datetime.datetime] = None,
) -> int:
    """Streak — số buổi liên tiếp gần nhất hoàn thành ĐÚNG HẠN (completed_at <=
    scheduled_end), tính từ buổi gần nhất đã tới hạn (scheduled_end <= now) lùi
    về quá khứ. Gãy ngay khi gặp 1 buổi bị miss hoặc hoàn thành trễ. Chỉ tính
    theo TỪNG TASK riêng (mặc định đã chọn — xem scope mục 6/v1)."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    relevant = sorted(
        (s for s in schedules if s.task_id == task_id and s.scheduled_end <= now),
        key=lambda s: s.scheduled_start,
        reverse=True,
    )
    streak = 0
    for s in relevant:
        if s.completed and s.completed_at is not None and s.completed_at <= s.scheduled_end:
            streak += 1
        else:
            break
    return streak


def compute_goal_progress(goal_id: str, tasks: List[Task]) -> tuple[int, int]:
    """(số Task-goal-directed đã done, tổng số) cho 1 Goal — derived, không lưu field."""
    linked = [t for t in tasks if t.goal_id == goal_id]
    done = sum(1 for t in linked if t.status == "done")
    return done, len(linked)


def active_schedule(task_id: str, schedules: List[FlexibleSchedule]) -> Optional[FlexibleSchedule]:
    """FlexibleSchedule đang 'chờ' (chưa completed, chưa dismissed) gần nhất của
    1 Task — mô hình tuần tự chỉ nên có tối đa 1 cái tại một thời điểm."""
    pending = [s for s in schedules if s.task_id == task_id and not s.completed and not s.dismissed]
    if not pending:
        return None
    return max(pending, key=lambda s: s.scheduled_start)


def missed_schedules(
    schedules: List[FlexibleSchedule], now: Optional[datetime.datetime] = None
) -> List[FlexibleSchedule]:
    """Các FlexibleSchedule đã qua scheduled_end mà chưa completed và chưa
    dismissed — nguồn dữ liệu cho Warning system. dismissed=True (người dùng
    đã chọn 'Bỏ qua') loại vĩnh viễn khỏi danh sách này, tránh dội cảnh báo
    vô hạn qua từng lần mở app."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return [s for s in schedules if not s.completed and not s.dismissed and s.scheduled_end < now]


def check_stale_tasks(
    tasks: List[Task],
    schedules: List[FlexibleSchedule],
    now: Optional[datetime.datetime] = None,
) -> List[Task]:
    """Kiểm tra và TỰ ĐỘNG pause các Task pending không hoạt động quá
    PAUSE_THRESHOLD_DAYS (không có FlexibleSchedule nào completed gần đây).
    Trả về danh sách Task VỪA bị pause trong lần gọi này (để main.py thông báo).
    Tự động pause, không chờ xác nhận — thông báo ở lần mở app kế tiếp
    (mặc định đã chọn, xem scope mục 6/v1)."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    newly_paused = []
    for t in tasks:
        if t.status != "pending":
            continue
        task_schedules = [s for s in schedules if s.task_id == t.id and s.completed and s.completed_at]
        if task_schedules:
            last_activity = max(s.completed_at for s in task_schedules)
        else:
            last_activity = t.created_at
        days_idle = (now - last_activity).days
        if days_idle >= PAUSE_THRESHOLD_DAYS:
            t.pause()
            newly_paused.append(t)
    return newly_paused