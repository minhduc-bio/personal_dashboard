from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# v0: chỉ đọc — không có scope ghi. Ghi ngược vào Calendar là v3, chưa mở ở đây.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Path tương đối theo project root (không hardcode path máy cá nhân như bản gốc
# "C:/Users/Admin/Downloads/..." — path đó vừa không portable vừa lộ thông tin máy).
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TOKEN_PATH = "token.json"
CREDS_PATH = "credentials.json"

HANOI_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def get_service():
    TOKEN_PATH.parent.mkdir(exist_ok=True)
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDS_PATH.exists():
                raise FileNotFoundError(
                    f"Không tìm thấy credentials.json tại {CREDS_PATH}. "
                    "Tải file OAuth Client credentials từ Google Cloud Console và đặt ở gốc project."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def get_today_schedule() -> list[dict]:
    """Đọc FixedSchedule của hôm nay từ Google Calendar, quy đổi giờ Hanoi (UTC+7).

    singleEvents=True đã tự expand recurring events (RRULE) thành từng instance
    riêng lẻ, nên không cần tự xử lý RRULE — đây là hành vi đúng của Google API,
    bản gốc vốn đã dùng đúng flag này.
    """
    service = get_service()

    now_hanoi = datetime.datetime.now(HANOI_TZ)
    start_of_day = now_hanoi.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + datetime.timedelta(days=1)

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    schedule = []
    for event in events_result.get("items", []):
        raw_start = event["start"].get("dateTime", event["start"].get("date"))
        raw_end = event["end"].get("dateTime", event["end"].get("date"))
        schedule.append({
            "summary": event.get("summary", "(không tên)"),
            "start": _to_hanoi_label(raw_start),
            "end": _to_hanoi_label(raw_end),
        })
    return schedule


def _to_hanoi_label(raw: str) -> str:
    """Chuyển ISO datetime (hoặc date all-day) sang giờ Hanoi để hiển thị.

    Bản gốc chỉ dùng UTC khi tính timeMin và không hề convert khi hiển thị,
    dù DoD trong 00_v0_scope.md đã tick sẵn mục "Timezone hiển thị đúng giờ Hanoi".
    """
    try:
        dt = datetime.datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=HANOI_TZ)
        return dt.astimezone(HANOI_TZ).strftime("%H:%M")
    except ValueError:
        # all-day event, raw dạng "YYYY-MM-DD"
        return "Cả ngày"


if __name__ == "__main__":
    for e in get_today_schedule():
        print(f"{e['start']}-{e['end']} | {e['summary']}")