import datetime
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.timezone import APP_TZ

# V0 — CHỈ ĐỌC. Không đổi scope này sang quyền ghi ở v0 (xem 00_v0_scope.md mục 2).
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Không hardcode path máy cá nhân (VD: C:/Users/Admin/...). Cho phép override bằng
# biến môi trường; mặc định tìm credentials.json ở thư mục gốc project, token lưu
# cùng chỗ với data khác của app để nhất quán với storage.py.
CREDS_PATH = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
TOKEN_PATH = os.environ.get("GOOGLE_TOKEN_PATH", str(DATA_DIR / "token.json"))


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


def list_upcoming_events(max_results=20):
    """Đọc FixedSchedule HÔM NAY từ Google Calendar (read-only), real-time theo giờ Hanoi:

    - Event chưa tới giờ bắt đầu: hiển thị bình thường với khung giờ start-end.
    - Event đang trong khoảng start <= now <= end: hiển thị kèm nhãn "Đang diễn ra".
    - Event đã qua giờ kết thúc (end < now): tự động ẩn khỏi danh sách trả về.
    - Event cả ngày (all-day, không có giờ cụ thể): luôn hiển thị, không áp dụng
      logic đang-diễn-ra/đã-kết-thúc vì không có mốc giờ để so sánh.

    singleEvents=True nên recurring events/RRULE đã được Google API tự expand
    thành từng instance riêng lẻ trước khi lọc.
    """
    service = get_service()
    now_hanoi = datetime.datetime.now(APP_TZ)
    start_of_day = now_hanoi.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + datetime.timedelta(days=1)

    events_result = service.events().list(
        calendarId="primary",
        # timeMin lấy từ đầu ngày (chứ không phải từ "now") để không bỏ sót
        # event đã bắt đầu trước "now" nhưng vẫn đang diễn ra tại thời điểm mở app.
        timeMin=start_of_day.astimezone(datetime.timezone.utc).isoformat(),
        timeMax=end_of_day.astimezone(datetime.timezone.utc).isoformat(),
        maxResults=max_results, singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = []
    for e in events_result.get("items", []):
        summary = e.get("summary", "(không tên)")
        start_raw = e["start"].get("dateTime", e["start"].get("date"))
        end_raw = e["end"].get("dateTime", e["end"].get("date"))

        start_dt = _parse_dt(start_raw)
        end_dt = _parse_dt(end_raw)

        if start_dt is None or end_dt is None:
            # all-day event -> không có giờ cụ thể để so sánh, luôn hiển thị
            events.append({"summary": summary, "start_display": "Cả ngày"})
            continue

        if end_dt < now_hanoi:
            # đã qua giờ kết thúc -> "xóa dòng" bằng cách không đưa vào kết quả
            continue

        start_str = start_dt.astimezone(APP_TZ).strftime("%H:%M")
        end_str = end_dt.astimezone(APP_TZ).strftime("%H:%M")
        time_range = f"{start_str} - {end_str}"
        if start_dt <= now_hanoi <= end_dt:
            time_range += " (🔴 Đang diễn ra)"

        events.append({"summary": summary, "start_display": time_range})

    return events


def _parse_dt(raw: str):
    """Parse chuỗi ISO datetime có offset (VD: '2026-08-07T09:00:00+07:00').
    Trả về None nếu đây là all-day event (chỉ có 'date', không có giờ/offset).
    """
    try:
        dt = datetime.datetime.fromisoformat(raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return None
    return dt


if __name__ == "__main__":
    for e in list_upcoming_events():
        print(e["start_display"], "-", e["summary"])