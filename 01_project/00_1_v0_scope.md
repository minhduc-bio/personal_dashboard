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

Không có: `Workspace`, `Project`, `Resource`, `ResourceLink`, `DailyReview`, `Note`, `Sandbox`, `PomodoroSession`, `TerminalSession`, `Goal` — tất cả các object này thuộc v1+ (xem mục 6).

## 2. V0 — Integration được phép

```text
Google Calendar API — READ-ONLY, scope: calendar.readonly
```

Không có: Gmail, Drive, Docs, Sheets, Google Tasks, OneNote. Không ghi ngược dữ liệu vào bất kỳ hệ thống ngoài nào ở v0 — chỉ đọc. (Ý định thêm "ghi Task vào Calendar" đã được cân nhắc và **chốt lùi về v3** — xem mục 6, lý do: cần mở scope OAuth ghi + thêm field thời gian vào Task, rủi ro ghi đè dữ liệu thật khi v0 chưa test ổn định.)

## 3. Nguyên tắc state của DailySession — không phải menu thủ công

`state` (`Created → Planning → Active → Reviewing → Closed`) **không được chọn tay qua UI**. Nó tự động tiến lên khi người dùng thực hiện đúng hành động tương ứng, mô phỏng chuỗi Start of Day → During Day → End of Day:

```text
Created    -> (đặt mood hoặc thêm task đầu tiên) -> Planning
Planning   -> (hoàn thành 1 task)                -> Active
Active     -> (chọn "Kết thúc ngày")             -> Reviewing -> Closed
```

State chỉ tiến, không lùi. Một khi `Closed`, phiên hôm đó không nhận thao tác nào khác ngoài thoát app.

## 4. Task Lifecycle (v0) — Task là Global entity

`Task` **không** gắn cứng vào 1 `DailySession`. Task chưa hoàn thành vẫn tồn tại nguyên vẹn khi sang ngày mới — không tự động xóa, không tự động "chuyển" thành task của ngày mới.

`Task.scheduled_date` là **single source of truth** cho việc task thuộc về ngày nào:

```text
scheduled_date = hôm nay          -> Today's Tasks
scheduled_date < hôm nay + pending -> Overdue
Chưa có scheduled_date            -> Unscheduled
```

`DailySession` không lưu danh sách Task của riêng nó (không có field `task_ids`) — tránh 2 nguồn sự thật lệch nhau (VD: task Overdue được hoàn thành hôm nay không nghĩa là nó "thuộc về" session hôm nay). Cuối ngày (`Kết thúc ngày`), số liệu tổng kết được derive trực tiếp từ `Task.completed_at`, không cần Session tham chiếu ngược.

**Complete và Delete tách biệt**, không gộp chung — khác ý nghĩa dữ liệu:

- Complete: giữ nguyên task, đổi `status`, ghi `completed_at` để tracking.
- Delete: xóa hẳn khỏi hệ thống, không giữ log (hard delete).

Overdue tích hợp trực tiếp vào "Xem công việc" (không có menu riêng). **Chưa có Reschedule** ở v0 — nếu trong lúc dùng thật thấy Overdue tồn đọng gây khó chịu (chỉ có 2 lựa chọn Complete/Delete cho task quá hạn nhưng chưa muốn làm), đó là tín hiệu cân nhắc thêm Reschedule sớm hơn kế hoạch.

### Timestamp & timezone

`created_at`/`completed_at` luôn lưu **UTC-aware datetime** — không tự convert giờ local ở tầng model. Muốn biết task/thời điểm thuộc "ngày nào" theo giờ người dùng, luôn đi qua `src/timezone.py::to_app_date()`, không so sánh trực tiếp `.date()` của timestamp UTC (sai lệch quanh mốc nửa đêm giờ Hanoi).

Timezone ứng dụng (`Asia/Ho_Chi_Minh`, hiện dùng fixed offset UTC+7) định nghĩa **một chỗ duy nhất**: `src/timezone.py` (`APP_TZ`). `models.py` và `calendar_client.py` import từ đây, không tự định nghĩa riêng.

## 5. V0 — Tiêu chí hoàn thành ("Definition of Done")

> Cập nhật 2026-08-07 (lần 2): Task Lifecycle ở mục 4 vừa thay đổi khá căn bản cách Task vận hành (Global thay vì ngầm-định gắn-theo-session, thêm Overdue, tách Complete/Delete) — **quyết định chủ đích reset lại DoD về chưa tick**, vì workflow đang được kiểm chứng đã đổi bản chất giữa chừng, không thể tính tiếp những ngày test trước đó.

- [ ] OAuth Calendar chạy được, refresh token không cần đăng nhập lại mỗi ngày _(cần vài ngày thật mới lộ ra)_
- [ ] Recurring events (RRULE) hiển thị đúng, không bị thiếu hoặc trùng lịch
- [ ] Timezone hiển thị đúng giờ Hanoi (UTC+7), kể cả quanh mốc nửa đêm
- [ ] `DailySession` đi hết vòng đời `Created → Planning → Active → Reviewing → Closed` mà không kẹt state (state tự động, xem mục 3)
- [ ] `Mood` (High/Neutral/Low) lọc được `Task` theo `mood_affinity` (chỉ áp cho Today/Unscheduled, Overdue luôn hiện đủ)
- [ ] Task Overdue/Today/Unscheduled hiển thị đúng nhóm, đúng theo giờ local
- [ ] Complete và Delete hoạt động đúng, không lẫn lộn ý nghĩa dữ liệu
- [ ] Dữ liệu `Task`, `Mood`, `DailySession` lưu local (JSON) — không mất dữ liệu khi tắt/mở lại app
- [ ] Đã tự chạy tay ít nhất 5-7 ngày liên tục để kiểm chứng workflow, không chỉ test 1 lần

**Chỉ khi tick hết mục trên mới được mở sang v1.**

## 6. Tương lai phát triển (sau khi v0 chạy ổn)

### v1 — Mở rộng domain, vẫn giữ tối giản UI

```text
+ Workspace (container tổng, chưa cần UI riêng)
+ Project (gắn Task vào nhiều DailySession)
+ ResourceLink (chỉ dạng đọc — mở file Drive/local, không edit tại chỗ)
+ DailyReview (rate mood/stress/achievement cuối ngày → ghi CSV)
+ Reschedule cho Task (nếu Overdue-không-Reschedule gây khó chịu thật trong lúc dùng v0)
+ Goal — Task — Schedule (domain model đầy đủ, xem chi tiết ngay dưới)
```

Vẫn CLI hoặc UI rất đơn giản. Mục tiêu v1: domain model đầy đủ hơn nhưng **chưa đụng vào UI thật**.

#### Domain model: Goal ≠ Task ≠ Schedule

Ba khái niệm tách biệt, không được gộp:

```text
Task     — đại diện cho công việc cần hoàn thành
Schedule — đại diện cho khoảng thời gian dành để thực hiện Task
Goal     — đại diện cho việc tracking progress
```

**Quan hệ:**

- 1 Task có thể có **nhiều** Schedule.
- 1 Goal có thể có **nhiều** Task (cụ thể là nhiều Task-goal-directed — xem dưới).
- Task tồn tại **độc lập** với Schedule — Schedule có thể được tạo, thay đổi, hoặc xóa mà **không làm mất Task**. Schedule chỉ tạo ra một khoảng thời gian cụ thể để thực hiện Task, không phải bản thân Task.

**Task-to-do vs Task-goal-directed — quan hệ tập con (subtype), không phải 2 loại loại-trừ-nhau:**

> Task-goal-directed là Task-to-do, nhưng Task-to-do không phải (bắt buộc) là Task-goal-directed.

- **Task-to-do**: có thể tự phát sinh trong ngày/tuần để giải quyết một việc cụ thể, không bắt buộc thuộc Goal nào, tồn tại độc lập, có thể Overdue trong 1 khoảng thời gian không quá cụ thể (ngày/tuần).
- **Task-goal-directed**: là Task-to-do có thêm ràng buộc — phải thuộc ít nhất 1 Goal, đóng vai trò checkpoint để tracking progress của Goal đó.

Vì đây là quan hệ tập con chứ không phải 2 class riêng biệt, cách mô hình hóa hợp lý nhất: `Task` thêm 1 field tùy chọn kiểu `goal_id: Optional[str]` — có giá trị nghĩa là Task-goal-directed, `None` nghĩa là Task-to-do thuần. **Không cần** tách thành 2 model/2 Literal type khác nhau.

**Goal:**

```text
Goal
├── Task-goal-directed
├── Task-goal-directed
└── ...
```

Người dùng set các checkpoint cho Goal chính là các Task-goal-directed này; progress của Goal hiển thị dựa trên completion của chúng.

**Lưu ý implement (khi tới lúc, KHÔNG phải bây giờ):**

- `Schedule` tách khỏi `Task` ở v1 thực chất là **thay thế** cách `Task.scheduled_date` đang hoạt động ở v0 (hiện là 1 field ngày đơn, gắn thẳng vào Task) — không phải cộng thêm bên cạnh. Khi lên v1, cần quyết định: giữ `scheduled_date` làm field tiện lợi (derive từ Schedule sớm nhất) hay bỏ hẳn, chuyển toàn bộ logic Overdue/Today/Unscheduled sang truy vấn qua bảng `Schedule` riêng.
- `Goal` là object hoàn toàn mới, chưa từng tồn tại ở v0 — cần model, storage, và ít nhất 1-2 action CRUD riêng (tạo Goal, gắn Task vào Goal, xem progress).

### v2 — UI thật (TypeScript, xây bằng Bolt AI)

```text
+ Giao diện Dashboard: Start of Day / During Day / End of Day
+ Mood picker dạng dialog
+ Calendar view (Today/Week/Month) kéo-thả Task vào Schedule
+ Kết nối UI với backend v0/v1 qua API nội bộ (REST hoặc tRPC)
```

Lưu ý khi vibe code UI bằng Bolt AI:

- Backend (auth, state machine) **giữ nguyên đã test ở v0/v1** — Bolt AI chỉ nên chạm vào phần UI/API layer, không viết lại logic domain đã ổn định.
- TypeScript giúp bắt lỗi kiểu dữ liệu giữa UI và API response (đặc biệt hữu ích khi domain model nhiều entity như `Goal`/`Task`/`Schedule` ở trên), nhưng không thay được việc test tay các luồng OAuth/timezone đã nêu ở mục 5.
- Nên định nghĩa API contract (request/response shape của `DailySession`, `Task`, `Mood`, `Goal`, `Schedule`) thành file `.ts` types **trước khi** để Bolt AI generate UI, để tránh UI và backend lệch schema.

### v3 — Ghi ngược & tích hợp mở rộng

```text
+ Ghi Task vào Google Calendar (không chỉ đọc)
+ Gmail preview (đọc), Drive file picker
+ Sandbox tạm cho note trong ngày
```

Đây là lúc rủi ro ghi-đè dữ liệu thật xuất hiện trở lại — chỉ mở sau khi v0-v2 đã dùng thật, ổn định. Điều kiện tối thiểu trước khi mở: đổi OAuth scope sang quyền ghi (`calendar` thay vì `calendar.readonly`), và `Task` cần thêm field thời gian (`deadline`, `estimated_duration`) để có đủ dữ liệu tạo Calendar Event hợp lệ.

### v4+ — Tính năng phụ trợ

```text
Pomodoro
Terminal integration
OneNote link
```

## 7. Nguyên tắc chống scope creep

- Mỗi lần muốn thêm object/integration mới: hỏi "đang ở v mấy?" — nếu chưa tick hết Definition of Done của v hiện tại, không thêm.
- Nếu AI (Claude, Bolt AI, hay bất kỳ) tự đề xuất thêm tính năng "cho tiện", đối chiếu với file này trước khi chấp nhận.
- File này có thể sửa, nhưng sửa là quyết định có chủ đích — không để nó tự phình ra qua từng prompt.
- Khi một thay đổi đủ lớn để làm thay đổi bản chất workflow đang test (như Task Lifecycle ở mục 4), reset lại đồng hồ DoD thay vì cộng dồn ngày test cũ — ngày test trên 1 workflow đã đổi bản chất không còn phản ánh đúng workflow hiện tại.
- Ý tưởng được ghi nhận vào mục "Tương lai phát triển" (như Goal-Task-Schedule ở mục 6) là **tài liệu thiết kế**, không phải giấy phép implement — vẫn phải chờ đúng version và đúng DoD mới bắt tay code.