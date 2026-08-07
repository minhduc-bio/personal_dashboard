


# Hướng dẫn sử dụng & Test 7 ngày — Personal Workspace v0 (MVP)

> Tài liệu này đi kèm `00_v0_scope.md`. Mục tiêu: dùng app thật mỗi ngày trong 7 ngày liên tục để tick nốt 2 mục DoD cần thời gian thật (`OAuth refresh token`, `chạy tay 5-7 ngày`), đồng thời tự quan sát các điểm UX còn nghi vấn trước khi quyết định mở sang v1.

---

# 1. Cài đặt lần đầu

## 1.1. Cấu trúc thư mục bắt buộc

```text
01_project/
├── main.py                  <- entry point, LUÔN chạy từ đây
├── credentials.json         <- OAuth credentials tải từ Google Cloud Console
├── data/                    <- tự tạo khi chạy lần đầu (tasks.json, sessions/, token.json)
└── src/
    ├── __init__.py
    ├── models.py
    ├── storage.py
    ├── calendar_client.py
    └── timezone.py
````

## 1.2. Cài thư viện

```powershell
pip install pydantic google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## 1.3. Chạy app

**Luôn đứng ở `01_project`, không đứng trong `src`:**

```powershell
cd C:\Users\Admin\Downloads\03_Dashboard\idea\01_project
python main.py
```

Lần đầu chạy menu `1` (Xem lịch), trình duyệt sẽ tự mở để bạn đăng nhập Google — chỉ cần làm 1 lần, sau đó `data/token.json` sẽ tự lưu lại.

---

# 2. Giải thích menu

|#|Chức năng|Ghi chú|
|---|---|---|
|1|Xem lịch Google Calendar|Chỉ đọc, chỉ hiện lịch **hôm nay**, tự ẩn event đã qua giờ kết thúc, đánh dấu 🔴 "Đang diễn ra" nếu đang trong khung giờ|
|2|Xem / đặt Mood hôm nay|Chọn số 1/2/3 (High/Neutral/Low). Đặt mood lần đầu trong ngày sẽ tự chuyển state phiên sang `Planning`|
|3|Thêm công việc mới|Nhập tên, chọn mood phù hợp, chọn có lên lịch cho hôm nay hay để "chưa lên lịch"|
|4|Xem công việc|Nhóm theo 🔴 Overdue / 🟡 Today / ⚪ Unscheduled. Có thể lọc theo mood (chỉ áp cho Today + Unscheduled — Overdue luôn hiện đủ)|
|5|Đánh dấu hoàn thành|Chọn task pending để complete — giữ lại dữ liệu, ghi `completed_at`|
|6|Xóa công việc|Xóa hẳn khỏi hệ thống — **không thể hoàn tác**, có bước xác nhận|
|7|Kết thúc ngày|Chuyển state sang `Reviewing` → `Closed`, in tổng kết số task hoàn thành hôm nay|
|8|Thoát và lưu|Thoát app|

Khi phiên đã `Closed`, menu rút gọn còn: thoát (`0`), hoặc `r` để mở lại phiên — **`r` chỉ dùng khi test, không dùng khi vận hành thật.**

---

# 3. Nhịp dùng hằng ngày (gợi ý)

## 3.1. Đầu ngày

1. Mở app, chọn `2` đặt mood.
    
2. Chọn `1` xem lịch hôm nay có gì.
    
3. Chọn `3` thêm các task muốn làm hôm nay (lên lịch = hôm nay).
    

## 3.2. Trong ngày

4. Mỗi khi xong việc, chọn `5` đánh dấu hoàn thành.
    
5. Thỉnh thoảng chọn `4` xem còn gì Overdue/Today/Unscheduled.
    
6. Task nào không còn cần thiết, chọn `6` xóa.
    

## 3.3. Cuối ngày

7. Chọn `7` kết thúc ngày, xem tổng kết.
    
8. Chọn `8` thoát.
    

Hôm sau mở lại app, `main.py` tự nhận diện ngày mới, tạo `DailySession` mới ở state `Created` — task Overdue từ hôm qua vẫn còn nguyên (Task là Global, không tự xóa/reset).

---

# 4. Nhật ký test 7 ngày

Điền lại mỗi ngày — đây là bằng chứng thực tế để tick DoD, không phải hình thức.

|Ngày|Đã dùng thật?|OAuth có phải đăng nhập lại không?|Vấn đề gặp phải|Ghi chú UX|
|---|---|---|---|---|
|1|||||
|2|||||
|3|||||
|4|||||
|5|||||
|6|||||
|7|||||

## 4.1. Các điểm cần chủ ý quan sát trong 7 ngày này

- **OAuth**: khoảng ngày 7-8 theo dõi xem có bị bắt đăng nhập lại không (do Google giới hạn refresh token ~7 ngày nếu OAuth consent screen đang ở "Testing" trên Google Cloud Console).
    
- **Overdue không có Reschedule**: nếu thấy khó chịu vì task Overdue chỉ có 2 lựa chọn Complete/Delete mà không muốn làm cả hai — ghi lại cụ thể tình huống, đây là tín hiệu để đưa Reschedule vào sớm hơn kế hoạch (dự kiến v1).
    
- **Danh sách "Xem công việc" có bị rối không** khi task done tích lũy nhiều ngày (hiện tại `list_tasks` chỉ hiện pending, không hiện done — task đã xong chỉ còn thấy trong menu Xóa).
    
- **Mood filter**: có thực sự dùng tới không, hay luôn bỏ qua bước lọc?
    
- **Timezone quanh nửa đêm**: nếu có lần thao tác gần 00:00, kiểm tra task/event có bị lệch ngày không.
    

---

# 5. Lỗi thường gặp

|Lỗi|Nguyên nhân|Cách xử lý|
|---|---|---|
|`ModuleNotFoundError: No module named 'src'`|Đang chạy `python main.py` hoặc `python calendar_client.py` từ **trong** thư mục `src`, hoặc `main.py` bị đặt nhầm vào `src`|Luôn `cd` về `01_project` (thư mục cha) rồi mới chạy `python main.py`|
|`ZoneInfoNotFoundError: No time zone found with key Asia/Ho_Chi_Minh`|Đã fix — app không còn dùng `zoneinfo`, chuyển sang fixed offset UTC+7 trong `src/timezone.py`|Nếu vẫn gặp, kiểm tra `calendar_client.py` có đang import đúng `from src.timezone import APP_TZ` không|
|`FileNotFoundError: Không tìm thấy credentials.json`|File OAuth credentials chưa đặt đúng chỗ|Đặt `credentials.json` ngay tại `01_project/`, hoặc set biến môi trường `GOOGLE_CREDENTIALS_PATH` trỏ tới đường dẫn khác|
|`ValidationError` khi load `tasks.json`|File `tasks.json` cũ được tạo từ phiên bản model trước (thiếu `scheduled_date`/`completed_at` dạng datetime)|Với dữ liệu test, đơn giản nhất là xóa `data/tasks.json` và `data/sessions/` để bắt đầu lại sạch — vì đang trong giai đoạn test, chưa phải dữ liệu cần giữ|
|Popup "Google chưa xác minh ứng dụng này" khi đăng nhập lại|OAuth consent screen đang ở chế độ "Testing"|Bình thường với app cá nhân — bấm "Advanced" → "Go to (tên app) (unsafe)" để tiếp tục|

---

# 6. Sau khi đủ 7 ngày

1. Mở `00_v0_scope.md`, đối chiếu từng dòng DoD ở mục 5 với nhật ký test ở mục 4 tài liệu này.
    
2. Tick `[x]` cho những mục thực sự đã xác nhận đúng — không tick nếu chưa chắc.
    
3. Nếu tick hết → quay lại yêu cầu Claude "chuyển sang v1", lúc đó mới bắt đầu thiết kế `Workspace`, `Project`, `ResourceLink`, `DailyReview`.
    
4. Nếu có mục chưa tick được (đặc biệt OAuth hoặc UX Overdue) → cứ nói rõ, xử lý điểm đó trước khi mở rộng thêm.
    

[[Future Implementation]]

---

# 7. Deferred Ideas & Documentation Consistency

[[Future Implementation]]

## 7.1. Documentation consistency

Kiểm tra documentation phải nhất quán với implementation hiện tại.

Đặc biệt:
- `scheduled_date`
- `completed_at`
- kiểu dữ liệu datetime
- timezone handling

Không refactor implementation chỉ để phục vụ documentation nếu behavior hiện tại đã đúng. Chỉ sửa wording/documentation khi mô tả không khớp với implementation.

---

## 7.2. Timezone awareness

Workspace sử dụng **Asia/Ho_Chi_Minh (UTC+7)** làm application timezone hiện tại.

Cần phân biệt:
- **Timestamp**: thời điểm chính xác mà action xảy ra.
- **Calendar date**: ngày mà action thuộc về theo timezone của người dùng.

Khi xác định Task được hoàn thành trong một `DailySession`:
1. Lấy `completed_at`.
2. Chuyển timestamp sang application timezone.
3. Lấy local calendar date.
4. So sánh với `session.date`.

Không so sánh trực tiếp ngày của UTC timestamp với `session.date`.

Trong 7 ngày test, chủ động quan sát:
- thao tác gần 00:00;
- Task hoàn thành ngay sau 00:00;
- Calendar Event nằm gần ranh giới giữa hai ngày;
- Task có bị phân loại nhầm sang ngày trước/sau hay không.

Nếu phát hiện lỗi timezone, ghi lại **thời điểm, action và kết quả thực tế** vào nhật ký test trước khi sửa.

---

## 7.3. Deferred ideas — không implement trong v0

Các ý tưởng dưới đây được ghi nhận để phát triển sau, **không implement trong vòng test v0**:

# Goal – Task – Schedule

**Goal ≠ Task ≠ Schedule**

- **Task** đại diện cho công việc cần hoàn thành.
- **Schedule** đại diện cho khoảng thời gian dành để thực hiện Task.
- **Goal** đại diện cho việc tracking progress.

## Relationships

- Một **Task** có thể có nhiều **Schedule**.
- Một **Goal** có thể có nhiều **Task-goal-directed**.
- Task tồn tại độc lập với Schedule.
- Schedule có thể được tạo, thay đổi hoặc xóa mà không làm mất Task.
- Schedule chỉ tạo ra một khoảng thời gian cụ thể để người dùng có thể thực hiện Task.

## Task types

Có hai loại Task:

### 1. Task-to-do

Task phát sinh để giải quyết một công việc cụ thể.

- Có thể phát sinh tự phát trong ngày hoặc trong tuần.
- Không bắt buộc thuộc một Goal.
- Có thể tồn tại độc lập.
- Có thể trở thành Overdue nếu đã được scheduled nhưng chưa hoàn thành.

### 2. Task-goal-directed

Task-to-do phục vụ trực tiếp cho một Goal.

- Phải thuộc ít nhất một Goal.
- Được sử dụng như một checkpoint để theo dõi tiến độ của Goal.
- Completion của các Task-goal-directed được sử dụng để biểu diễn progress của Goal.

### Goal

Goal là lớp abstraction cao hơn Task.

```text
Goal
 ├── Task-goal-directed
 ├── Task-goal-directed
 ├── Task-goal-directed
 └── ...