import json
from pathlib import Path
from typing import List, Optional

# Nạp "bản vẽ" từ models.py
from src.models import Task, Session

# Định nghĩa các đường dẫn thư mục lưu trữ
BASE_DIR = Path("data")
TASKS_FILE = BASE_DIR / "tasks.json"
SESSIONS_DIR = BASE_DIR / "sessions"


def init_storage():
    """Khởi tạo thư mục và file JSON cơ bản nếu chưa tồn tại trên máy."""
    BASE_DIR.mkdir(exist_ok=True)
    SESSIONS_DIR.mkdir(exist_ok=True)

    # Nếu chưa có file tasks.json, tạo một file chứa mảng rỗng []
    if not TASKS_FILE.exists():
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


# ==========================================
# CÁC HÀM XỬ LÝ CÔNG VIỆC (TASK)
# ==========================================

def load_tasks() -> List[Task]:
    """Đọc dữ liệu từ tasks.json và biến nó thành các object Task."""
    if not TASKS_FILE.exists():
        return []

    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        # Chuyển đổi từng dict trong list JSON thành object Pydantic Task
        return [Task(**item) for item in data]


def save_tasks(tasks: List[Task]):
    """Lưu danh sách object Task xuống file tasks.json."""
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        # mode="json" bắt buộc ở đây: Task giờ có field datetime/date
        # (created_at, completed_at, scheduled_date) — mode="json" tự convert
        # chúng thành chuỗi ISO hợp lệ để json.dump() không lỗi.
        data = [task.model_dump(mode="json") for task in tasks]
        json.dump(data, f, ensure_ascii=False, indent=2)


# ==========================================
# CÁC HÀM XỬ LÝ PHIÊN LÀM VIỆC (SESSION)
# ==========================================

def load_session(date_str: str) -> Optional[Session]:
    """Tìm và đọc file Session theo ngày (VD: 2026-08-06.json)."""
    session_file = SESSIONS_DIR / f"{date_str}.json"
    if not session_file.exists():
        return None

    with open(session_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        return Session(**data)


def save_session(session: Session):
    """Lưu object Session xuống file (tên file là ngày của session đó)."""
    session_file = SESSIONS_DIR / f"{session.date}.json"
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session.model_dump(), f, ensure_ascii=False, indent=2)


def get_or_create_session(date_str: str) -> Session:
    """Lấy Session của ngày `date_str`; nếu ngày đó chưa từng chạy app,
    tạo mới một Session ở state 'Created' và lưu lại ngay.

    Đây là nơi xử lý case main.py trước đây gọi load_session() không có
    tham số và không xử lý kết quả None — nay được gom về một điểm duy nhất.
    """
    session = load_session(date_str)
    if session is None:
        session = Session(date=date_str)
        save_session(session)
    return session