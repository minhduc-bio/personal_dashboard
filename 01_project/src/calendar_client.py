import datetime
import os
from pathlib import Path
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# V0 — CHỈ ĐỌC. Không đổi scope này sang quyền ghi ở v0 (xem 00_v0_scope.md mục 2).
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Không hardcode path máy cá nhân (VD: C:/Users/Admin/...). Cho phép override bằng
# biến môi trường; mặc định tìm credentials.json ở thư mục gốc project, token lưu
# cùng chỗ với data khác của app để nhất quán với storage.py.
CREDS_PATH = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
TOKEN_PATH = os.environ.get("GOOGLE_TOKEN_PATH", str(DATA_DIR / "token.json"))

HANOI_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def get_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_PATH):
                raise FileNotFoundError(
                    f"Không tìm thấy credentials.json tại '{CREDS_PATH}'. "
                    "Đặt file ở thư mục gốc project hoặc set biến môi trường "
                    "GOOGLE_CREDENTIALS_PATH trỏ tới đường dẫn đúng."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def list_upcoming_events(max_results=10):
    """Đọc FixedSchedule từ Google Calendar (read-only, singleSevents=True nên
    recurring events/RRULE đã được Google API tự expand thành từng instance).
    Trả về list dict đã convert giờ hiển thị sang Hanoi (UTC+7).
    """
    service = get_service()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    events_result = service.events().list(
        calendarId="primary", timeMin=now,
        maxResults=max_results, singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = []
    for e in events_result.get("items", []):
        start_raw = e["start"].get("dateTime", e["start"].get("date"))
        events.append({
            "summary": e.get("summary", "(không tên)"),
            "start_display": _format_hanoi(start_raw),
        })
    return events


def _format_hanoi(start_raw: str) -> str:
    """Convert ISO datetime (có offset) sang giờ Hanoi để hiển thị.
    Event dạng all-day chỉ có 'date' (không có time) thì giữ nguyên.
    """
    try:
        dt = datetime.datetime.fromisoformat(start_raw)
    except ValueError:
        return start_raw
    if dt.tzinfo is None:
        # all-day event parse ra naive date -> không có timezone để convert
        return start_raw
    return dt.astimezone(HANOI_TZ).strftime("%Y-%m-%d %H:%M")


if __name__ == "__main__":
    for e in list_upcoming_events():
        print(e["start_display"], "-", e["summary"])