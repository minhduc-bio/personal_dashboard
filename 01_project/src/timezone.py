"""Timezone dùng chung cho toàn bộ app.

Single source of truth — models.py, calendar_client.py, main.py đều import
APP_TZ từ đây, không tự định nghĩa riêng lẻ.

Dùng fixed offset thay vì zoneinfo.ZoneInfo("Asia/Ho_Chi_Minh"): Windows không
có sẵn IANA tzdata (cần cài thêm package `tzdata` mới chạy được), còn Việt Nam
không áp dụng DST nên UTC+7 cố định là chính xác quanh năm, không cần phụ
thuộc thêm gì ngoài thư viện chuẩn.

Đổi timezone ứng dụng: chỉ cần sửa 1 dòng dưới đây.
"""
import datetime

APP_TZ = datetime.timezone(datetime.timedelta(hours=7))  # Asia/Ho_Chi_Minh


def to_app_date(dt: datetime.datetime) -> datetime.date:
    """Convert 1 datetime UTC-aware sang local calendar date theo APP_TZ.

    Đây là cách BẮT BUỘC để so sánh một timestamp (created_at, completed_at —
    luôn lưu dưới dạng UTC) với session.date (một local calendar date) —
    không bao giờ so sánh trực tiếp phần .date() của timestamp UTC, vì quanh
    mốc nửa đêm giờ Hanoi, ngày UTC và ngày local có thể lệch nhau 1 ngày.
    """
    return dt.astimezone(APP_TZ).date()