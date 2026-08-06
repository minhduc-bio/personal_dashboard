# Hướng dẫn từng bước: Setup & Build v0 — Personal Workspace

> Đi kèm với `00_v0_scope.md`. Đừng bỏ qua bước nào — mỗi bước sau đều phụ thuộc bước trước.

---

## Giai đoạn 1 — Google Cloud & OAuth

### 1.1. Tạo project

1. Vào https://console.cloud.google.com/
2. Góc trên → **New Project** → đặt tên (ví dụ `personal-workspace-v0`) → Create

### 1.2. Bật Calendar API

1. Menu trái → **APIs & Services → Library**
2. Tìm "Google Calendar API" → **Enable**

### 1.3. Cấu hình OAuth consent screen

1. **APIs & Services → OAuth consent screen**
2. User type: **External** (nếu bạn dùng Gmail cá nhân)
3. Điền tên app, email liên hệ → Save
4. Ở mục **Test users**, thêm chính email bạn dùng để test (bắt buộc — nếu không app sẽ báo lỗi "access denied" khi login)
5. Scope: thêm đúng `https://www.googleapis.com/auth/calendar.readonly` — không thêm scope nào khác

### 1.4. Tạo OAuth Client ID

1. **APIs & Services → Credentials → Create Credentials → OAuth client ID**
2. Application type: **Desktop app**
3. Tải file `credentials.json` về, đặt vào thư mục project (bước 2)

⚠️ Ngay lập tức thêm `credentials.json` và `token.json` vào `.gitignore` — không bao giờ commit file này lên GitHub.

---

## Giai đoạn 2 — Setup môi trường code

```bash
mkdir personal-workspace-v0 && cd personal-workspace-v0
git init
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

echo "google-api-python-client
google-auth-httplib2
google-auth-oauthlib" > requirements.txt

pip install -r requirements.txt
```

Tạo `.gitignore`:

```
venv/
credentials.json
token.json
data/
__pycache__/
```

Cấu trúc thư mục ban đầu:

```
personal-workspace-v0/
├── credentials.json
├── requirements.txt
├── data/                  # DailySession, Mood, Task lưu ở đây (JSON)
├── src/
│   ├── calendar_client.py
│   ├── storage.py
│   ├── models.py
│   └── main.py
└── 00_v0_scope.md
```

---

## Giai đoạn 3 — Script test OAuth đầu tiên (bước quan trọng nhất)

**Mục tiêu:** xác nhận đọc được Calendar thật trước khi xây bất cứ thứ gì khác lên trên. Tạo `src/calendar_client.py`:

```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os, datetime

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TOKEN_PATH = "token.json"
CREDS_PATH = "credentials.json"

def get_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def list_upcoming_events(max_results=10):
    service = get_service()
    now = datetime.datetime.utcnow().isoformat() + "Z"
    events_result = service.events().list(
        calendarId="primary", timeMin=now,
        maxResults=max_results, singleEvents=True,
        orderBy="startTime"
    ).execute()
    return events_result.get("items", [])

if __name__ == "__main__":
    events = list_upcoming_events()
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date"))
        print(start, "-", e.get("summary", "(không tên)"))
```

Chạy thử:

```bash
python src/calendar_client.py
```

- Lần đầu sẽ mở browser để bạn đăng nhập tài khoản test → cấp quyền → tạo `token.json`.
- Kiểm tra: có event lặp lại (recurring) hiển thị đúng không, giờ hiển thị có đúng giờ Hanoi (UTC+7) không.

**Nếu bước này chưa chạy đúng, dừng lại — không sang giai đoạn 4.**

---

## Giai đoạn 4 — Schema dữ liệu local

Tạo `src/models.py` định nghĩa schema (viết tay trước, không để AI tự bịa):

```python
# data/tasks.json
{
  "id": "t001",
  "title": "Viết báo cáo tuần",
  "mood_affinity": "High",       # High | Neutral | Low
  "status": "pending",           # pending | done
  "created_at": "2026-08-06"
}

# data/sessions/2026-08-06.json
{
  "date": "2026-08-06",
  "state": "Planning",           # Created|Planning|Active|Reviewing|Closed
  "mood": null,
  "task_ids": []
}
```

---

## Giai đoạn 5 — Vibe coding phần còn lại bằng Claude free chat

Vì free plan không có Claude Code, quy trình sẽ là **copy-paste có kiểm soát**, không phải agentic tự động:

1. Mở 1 cuộc chat riêng cho project này (giữ persistent để không phải giải thích lại)
2. **Prompt đầu tiên trong chat đó** — dán nguyên nội dung `00_v0_scope.md` + đoạn code `calendar_client.py` đã chạy được, nói rõ: _"Đây là scope đã chốt, đây là code OAuth đã test — chỉ viết thêm phần X, không thêm object hay integration nào khác"_
3. Thứ tự nên yêu cầu code, từng phần một, test xong mới sang phần sau:
    - `storage.py` (đọc/ghi JSON cho Task, DailySession)
    - `models.py` (class Task, DailySession, Mood + logic transition state)
    - CLI đơn giản trong `main.py` (menu: xem task theo mood, chuyển state session)
4. Sau mỗi đoạn code AI đưa ra: copy vào file, chạy thử ngay, không copy tiếp đoạn sau nếu đoạn này chưa chạy được
5. Nếu hết quota chat free giữa lúc đang làm, đợi reset (4-8 giờ) — đừng mở đoạn chat mới để né quota, vì sẽ mất context đã feed ở bước 2

---

## Giai đoạn 6 — Checklist test tay (đối chiếu với `00_v0_scope.md` mục 3)

Thực hiện thủ công, ghi kết quả:

- [ ] Tắt/mở lại token vẫn còn hiệu lực (không phải login lại)
- [ ] Recurring event hiển thị đủ, không trùng
- [ ] Giờ hiển thị đúng UTC+7
- [ ] Đi hết vòng đời DailySession 1 lần thủ công qua CLI
- [ ] Test lọc Task theo Mood cho cả 3 mood
- [ ] Tắt máy, mở lại, dữ liệu Task/Session không mất
- [ ] Dùng liên tục thật 5-7 ngày

Khi tick hết → v0 hoàn thành, quay lại phần "v1" trong `00_v0_scope.md` để mở rộng tiếp.