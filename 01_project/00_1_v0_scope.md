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

> Cập nhật 2026-08-07 (lần 3): v1 ban đầu gộp 7 khoản khác nhau — quá lớn cho 1 version. Tách lại thành **v1** (chỉ Goal + FlexibleSchedule + Warning/Pause system) và **v1.5** (phần còn lại của kế hoạch v1 cũ). `Schedule` KHÔNG phải Google Calendar event — xem lý do tách bạch ở phần "FlexibleSchedule" dưới đây.

### v1 — Goal + FlexibleSchedule + Warning/Pause system

```text
+ Goal (object mới)
+ FlexibleSchedule (object mới — native app, KHÔNG phải Google Calendar event)
+ Task: thêm goal_id (Optional), status có thêm "paused"
+ Warning system (tự động, hiện khi có Schedule bị miss)
+ Pause/Resume system (Task tự pause sau N ngày không hoạt động)
```

Vẫn CLI, chưa đụng UI thật.

#### Vì sao FlexibleSchedule tách khỏi Google Calendar (FixedSchedule)

Ý tưởng ban đầu là dùng thẳng Calendar event làm Schedule, nhưng va vào giới hạn kiến trúc: `calendar.readonly` (mục 2) cấm mọi ghi, kể cả ghi trạng thái "đã hoàn thành" lên event, và app không thể tự tạo event mới khi Schedule bị miss (cần quyền ghi, đã chốt lùi về v3). Nên tách 2 khái niệm:

|**Tiêu chí**|**FixedSchedule (giữ nguyên từ v0)**|**FlexibleSchedule (mới, v1)**|
|---|---|---|
|**Nguồn dữ liệu**|Google Calendar (đọc từ ngoài)|App tự quản lý hoàn toàn|
|**Ai tạo**|Người dùng tự tạo trên Calendar|App tự tạo khi người dùng xác nhận "muốn làm tiếp"|
|**Mục đích**|Xem cam kết cố định (họp, hẹn...)|Track ý định làm Task vào lúc nào|
|**Ghi/sửa**|Không (readonly)|Có — dữ liệu nội bộ app|

#### Mô hình: tuần tự (attempt log), không phải N-N linh hoạt

Tại một thời điểm, mỗi Task có **tối đa 1 FlexibleSchedule đang "chờ"** (pending). Khi Schedule đó bị miss (qua giờ kết thúc mà chưa complete), Task được đánh dấu "đã miss lần này"; người dùng được hỏi có muốn tạo Schedule mới (dời sang khi nào) hay bỏ qua. Đây **không phải** quan hệ nhiều-nhiều tự do kiểu đặt trước nhiều buổi cùng lúc — chọn tuần tự vì: (1) khớp đúng ví dụ gốc bạn đưa ra, (2) Warning tự động (Q5) đơn giản hơn hẳn — chỉ cần hỏi "Schedule đang chờ của Task này đã qua giờ chưa", (3) giữ v1 ở mức CLI, không cần màn hình quản lý lịch riêng.

#### Warning system

- **Header (tự động, mọi lần mở app):** 1 dòng ngắn nếu có Schedule bị miss chưa xử lý. VD: `⚠️ 2 lịch bị bỏ lỡ`.
- **Chi tiết (khi vào "Xem công việc" hoặc chọn xử lý trực tiếp):** prompt đầy đủ — _"Dời sang khi nào? (1) Ngày mai cùng giờ (2) Chọn ngày/giờ khác (3) Bỏ qua"_.
- Không chặn màn hình (không phải modal bắt buộc OK) — cảnh báo luôn hiện diện nhưng không cưỡng ép xử lý ngay.

#### Pause system

- Ngưỡng pause: **10 ngày liên tục không có Schedule nào được complete** (tính từ lần complete gần nhất, hoặc `created_at` nếu chưa từng complete) — cấu hình qua 1 hằng số (`PAUSE_THRESHOLD_DAYS`), không hardcode rải rác.
- Pause diễn ra **tự động** khi đạt ngưỡng (không chờ xác nhận), rồi thông báo ở lần mở app kế tiếp. Lý do: nếu chờ xác nhận, người dùng đang né tránh sẽ càng dễ bấm lơ thông báo. "Chọn từ bỏ" (theo đúng triết lý bạn đặt ra) diễn ra ở bước **Resume**, không phải ở bước Pause.
- Task `paused` được nhóm riêng trong "Xem công việc": **⏸️ Paused** — không xóa, không lẫn với 🔴🟡⚪.
- Action **"Tiếp tục" (Resume)**: `paused → pending`, đồng thời mở ngay prompt tạo FlexibleSchedule mới — quay lại luôn đi kèm 1 cam kết cụ thể, không "để đó tính sau" mơ hồ.

#### Task-goal-directed & Goal

> Task-goal-directed là Task-to-do, nhưng Task-to-do không phải (bắt buộc) là Task-goal-directed.

`Task` thêm field `goal_id: Optional[str]` — có giá trị nghĩa là Task-goal-directed (checkpoint của 1 Goal), `None` nghĩa là Task-to-do thuần. Không tách 2 model/2 Literal type riêng.

```text
Goal
├── Task-goal-directed
├── Task-goal-directed
└── ...
```

#### Progress — derived, không lưu field riêng

- `Goal.progress` = % Task-goal-directed (theo `goal_id`) đã `done`.
- `Task.progress` = % FlexibleSchedule của Task đó đã hoàn thành (VD hiển thị: `Task A [3/5 buổi đã hoàn thành]`).
- Hoàn thành 1 FlexibleSchedule **không** tự động đánh dấu Task `done` — 2 việc tách biệt hoàn toàn (complete Schedule = điểm danh 1 buổi; complete Task = qua menu Complete như v0).
- Cả 2 progress đều tính lúc hiển thị (derived), không lưu thành field — tránh 2 nguồn sự thật (lý do tương tự việc bỏ `session.task_ids` ở mục 4).

#### Không migrate dữ liệu từ v0

Dữ liệu test 5-7 ngày ở v0 là dữ liệu test thuần, chưa có impact thật — khi lên v1, xóa `data/` và bắt đầu sạch, không viết script chuyển `Task.scheduled_date` → `FlexibleSchedule`.

### v1.5 — Phần còn lại của kế hoạch v1 cũ

```text
+ Workspace (container tổng, chưa cần UI riêng)
+ Project (gắn Task vào nhiều DailySession)
+ ResourceLink (chỉ dạng đọc — mở file Drive/local, không edit tại chỗ)
+ DailyReview (rate mood/stress/achievement cuối ngày → ghi CSV)
```

Reschedule (từng dự kiến ở v1 cũ) coi như đã được giải quyết một phần bởi FlexibleSchedule ở v1 — "dời sang khi nào" chính là hành vi reschedule.

### v2 — UI thật (TypeScript, xây bằng Bolt AI)

```text
+ Giao diện Dashboard: Start of Day / During Day / End of Day
+ Mood picker dạng dialog
+ Calendar view (Today/Week/Month) kéo-thả Task vào FlexibleSchedule
+ Kết nối UI với backend v0/v1/v1.5 qua API nội bộ (REST hoặc tRPC)
```

Lưu ý khi vibe code UI bằng Bolt AI:

- Backend (auth, state machine, Warning/Pause logic) **giữ nguyên đã test ở các version trước** — Bolt AI chỉ nên chạm vào phần UI/API layer, không viết lại logic domain đã ổn định.
- TypeScript giúp bắt lỗi kiểu dữ liệu giữa UI và API response (đặc biệt hữu ích khi domain nhiều entity như `Goal`/`Task`/`FlexibleSchedule` ở trên), nhưng không thay được việc test tay các luồng OAuth/timezone/Pause đã nêu.
- Nên định nghĩa API contract (`DailySession`, `Task`, `Mood`, `Goal`, `FlexibleSchedule`) thành file `.ts` types **trước khi** để Bolt AI generate UI, tránh UI và backend lệch schema.

### v3 — Ghi ngược & tích hợp mở rộng

```text
+ Ghi Task vào Google Calendar (không chỉ đọc)
+ Gmail preview (đọc), Drive file picker
+ Sandbox tạm cho note trong ngày
```

Đây là lúc rủi ro ghi-đè dữ liệu thật xuất hiện trở lại — chỉ mở sau khi các version trước đã dùng thật, ổn định. Điều kiện tối thiểu trước khi mở: đổi OAuth scope sang quyền ghi (`calendar` thay vì `calendar.readonly`), và `Task` cần thêm field thời gian (`deadline`, `estimated_duration`) để có đủ dữ liệu tạo Calendar Event hợp lệ.

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
- Ý tưởng được ghi nhận vào mục "Tương lai phát triển" (như Goal-Task-FlexibleSchedule ở mục 6) là **tài liệu thiết kế**, không phải giấy phép implement — vẫn phải chờ đúng version và đúng DoD mới bắt tay code.
- Chỗ nào trong tài liệu còn đánh dấu ⚠️ **CẦN XÁC NHẬN LẠI**, không code phần đó cho tới khi được xác nhận tường minh — không tự suy diễn "chắc là đồng ý" từ việc im lặng.