Dựa vào **Scope Contract hiện tại**, mình sẽ đặt phần này ở **v1**, nhưng tách rõ mức độ của từng ý:

|Concept|Version|Lý do|
|---|---|---|
|**Goal**|**v1**|Đây là domain object phục vụ tracking progress, phù hợp với giai đoạn mở rộng domain|
|**Task-goal-directed**|**v1**|Đây là thuộc tính/relationship của Task với Goal, cần tồn tại cùng Goal|
|**Goal → nhiều Task**|**v1**|Là relationship cốt lõi của Goal|
|**Goal checkpoints**|**v1**|Chính là cách Goal biểu diễn progress|
|**Schedule entity đầy đủ**|**v2**|v2 đã có Calendar view và kéo-thả Task vào Schedule|
|**Schedule → Google Calendar Event**|**v3**|v3 mới mở quyền ghi Calendar|
|**Task + Schedule tạo đồng thời trên Google Calendar**|**v3**|Đây là write-back workflow|

Điều này khớp khá đẹp với Scope Contract hiện tại: **v1 được dành cho mở rộng domain**, còn v2 mới xây UI Calendar/Schedule, và v3 mới ghi ngược vào Google Calendar.

### Nhưng có một điểm mình sẽ sửa trong cách gọi `Project`

Hiện v1 của bạn đã ghi:

> `Project (gắn Task vào nhiều DailySession)`

Trong khi concept mới là:

```text
Goal
 ├── Task
 ├── Task
 └── Task
```

Hai cái này **không hoàn toàn cùng abstraction**.

Mình sẽ chưa vội quyết định `Goal` = `Project`. Nhưng trước khi bắt đầu v1, bạn cần xác định:

```text
Project = một container của công việc?
Goal    = một desired outcome có progress?
```

Nếu đúng như vậy thì **cả Project và Goal có thể cùng tồn tại**.

Ví dụ:

```text
Goal:
"Hoàn thành R4DS"

Project:
"R4DS Learning"

Goal
 ├── Task: Chapter 3
 ├── Task: ggplot practice
 └── Task: Chapter 4
```

Trong khi Project có thể tổ chức nhiều loại Task/resource/workflow khác nhau.

---

### Còn v0 hiện tại: tuyệt đối chưa làm Goal

Scope Contract đã đặt nguyên tắc rất rõ: v0 chỉ có 4 object được phép tồn tại và chỉ khi hoàn thành DoD mới mở v1.

Vì vậy mình sẽ ghi trong deferred ideas:

```md
### Future: Goal

Target version: v1

Goal là domain object dùng để tracking progress.

- Một Goal có nhiều Task-goal-directed.
- Task-goal-directed phải thuộc ít nhất một Goal.
- Task-to-do không bắt buộc thuộc Goal.
- Các Task-goal-directed đóng vai trò checkpoint của Goal.
- Goal progress được derive từ trạng thái của các checkpoint.

Không implement trong v0.
```

Và:

```md
### Future: Schedule

Target version: v2

- Task ≠ Schedule.
- Một Task có thể có nhiều Schedule.
- Schedule đại diện cho time allocation để thực hiện Task.
- Schedule có thể thay đổi/xóa mà không xóa Task.
- v2 Calendar UI sẽ là nơi Schedule trở thành interaction thực tế.

Không implement trong v0/v1 nếu chưa cần.
```

**Tóm lại: `Goal = v1`, `Schedule = v2`, `Calendar write-back = v3`.**

Đây là một phân tầng khá đẹp: **v1 trả lời "tôi đang hướng tới cái gì?", v2 trả lời "tôi dành thời gian cho nó thế nào?", v3 trả lời "tôi ghi cam kết đó vào hệ thống bên ngoài thế nào?"**.

v0
Core workflow
Task / Mood / DailySession / Calendar READ

v1
Domain expansion
Routine / Goal / Project / DailyReview

v2
Real UI
Dashboard / Calendar interaction

v3
Calendar WRITE + integrations
Task ↔ Schedule ↔ Google Calendar

v4+
Personal Analytics & Self Review
────────────────────────────────
Historical data
Habit / Routine analysis
Goal progress
Behavioral patterns
Export → R / Python
Monthly / yearly self-review