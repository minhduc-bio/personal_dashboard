# Scope Contract — Personal Workspace v0

> Mục đích file này: là "hợp đồng scope" — bất cứ khi nào code (do bạn hoặc AI viết) có xu hướng thêm tính năng ngoài danh sách dưới, dừng lại và quay về file này trước.

---

## 1. V0 — Object được phép tồn tại (chỉ 4, không hơn)

```text
DailySession
Mood
Task
Schedule (chỉ FixedSchedule — đọc từ Google Calendar)
```

Không có: `Workspace`, `Project`, `Resource`, `ResourceLink`, `DailyReview`, `Note`, `Sandbox`, `PomodoroSession`, `TerminalSession` — tất cả các object này thuộc v1+ (xem mục 4).

## 2. V0 — Integration được phép

```text
Google Calendar API — READ-ONLY, scope: calendar.readonly
```

Không có: Gmail, Drive, Docs, Sheets, Google Tasks, OneNote. Không ghi ngược dữ liệu vào bất kỳ hệ thống ngoài nào ở v0 — chỉ đọc.

## 3. V0 — Tiêu chí hoàn thành ("Definition of Done")

- [x] OAuth Calendar chạy được, refresh token không cần đăng nhập lại mỗi ngày
- [x] Recurring events (RRULE) hiển thị đúng, không bị thiếu hoặc trùng lịch
- [x] Timezone hiển thị đúng giờ Hanoi (UTC+7)
- [x] `DailySession` đi hết vòng đời `Created → Planning → Active → Reviewing → Closed` mà không kẹt state
- [x] `Mood` (High/Neutral/Low) lọc được `Task` theo `mood_affinity`
- [x] Dữ liệu `Task`, `Mood`, `DailySession` lưu local (JSON/Markdown) — không mất dữ liệu khi tắt/mở lại app
- [x] Đã tự chạy tay ít nhất 5-7 ngày liên tục để kiểm chứng workflow, không chỉ test 1 lần

**Chỉ khi tick hết mục trên mới được mở sang v1.**

## 4. Tương lai phát triển (sau khi v0 chạy ổn)

### v1 — Mở rộng domain, vẫn giữ tối giản UI
```text
+ Workspace (container tổng, chưa cần UI riêng)
+ Project (gắn Task vào nhiều DailySession)
+ ResourceLink (chỉ dạng đọc — mở file Drive/local, không edit tại chỗ)
+ DailyReview (rate mood/stress/achievement cuối ngày → ghi CSV)
```
Vẫn CLI hoặc UI rất đơn giản. Mục tiêu v1: domain model đầy đủ hơn nhưng **chưa đụng vào UI thật**.

### v2 — UI thật (TypeScript, xây bằng Bolt AI)
```text
+ Giao diện Dashboard: Start of Day / During Day / End of Day
+ Mood picker dạng dialog
+ Calendar view (Today/Week/Month) kéo-thả Task vào Schedule
+ Kết nối UI với backend v0/v1 qua API nội bộ (REST hoặc tRPC)
```
Lưu ý khi vibe code UI bằng Bolt AI:
- Backend (auth, state machine) **giữ nguyên đã test ở v0/v1** — Bolt AI chỉ nên chạm vào phần UI/API layer, không viết lại logic domain đã ổn định.
- TypeScript giúp bắt lỗi kiểu dữ liệu giữa UI và API response (đặc biệt hữu ích khi domain model nhiều entity như trong `04_domain_model.md`), nhưng không thay được việc test tay các luồng OAuth/timezone đã nêu ở mục 3.
- Nên định nghĩa API contract (request/response shape của `DailySession`, `Task`, `Mood`) thành file `.ts` types **trước khi** để Bolt AI generate UI, để tránh UI và backend lệch schema.

### v3 — Ghi ngược & tích hợp mở rộng
```text
+ Ghi Task vào Google Calendar (không chỉ đọc)
+ Gmail preview (đọc), Drive file picker
+ Sandbox tạm cho note trong ngày
```
Đây là lúc rủi ro ghi-đè dữ liệu thật xuất hiện trở lại — chỉ mở sau khi v0-v2 đã dùng thật, ổn định.

### v4+ — Tính năng phụ trợ
```text
Pomodoro
Terminal integration
OneNote link
```

## 5. Nguyên tắc chống scope creep

- Mỗi lần muốn thêm object/integration mới: hỏi "đang ở v mấy?" — nếu chưa tick hết Definition of Done của v hiện tại, không thêm.
- Nếu AI (Claude, Bolt AI, hay bất kỳ) tự đề xuất thêm tính năng "cho tiện", đối chiếu với file này trước khi chấp nhận.
- File này có thể sửa, nhưng sửa là quyết định có chủ đích — không để nó tự phình ra qua từng prompt.
