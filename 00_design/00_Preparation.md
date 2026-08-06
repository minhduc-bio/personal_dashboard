Được. Tôi sẽ gom lại thành một **bộ từ điển thiết kế cho chính dự án của bạn**, thay vì giải thích các thuật ngữ một cách chung chung. Sau đó tôi sẽ chốt thành một quy trình cụ thể: **bây giờ cần làm gì, chưa cần làm gì, và khi nào mới được code**.

---

# I. Các thuật ngữ thiết kế cốt lõi

## 1. Product Definition

**Product Definition** = định nghĩa sản phẩm.

Nó trả lời:

> “Tôi đang xây cái gì, cho ai, để giải quyết vấn đề nào?”

Trong dự án của bạn:

> Một môi trường làm việc cá nhân thống nhất, kết hợp Google Workspace, local filesystem và các service xử lý để hỗ trợ chu trình lập kế hoạch → thực hiện → review → lập kế hoạch tiếp theo.

Nó **không phải technical specification**.

Không nên viết:

> “Ứng dụng sử dụng Electron + TypeScript + Python + PostgreSQL.”

Đó là implementation.

Product Definition phải đứng trước công nghệ.

---

# 2. Domain

**Domain** = phạm vi vấn đề mà application đang giải quyết.

Ví dụ domain của bạn là:

```text
Personal Work Management
```

Trong đó có các lĩnh vực:

```text
Communication
Planning
Task Management
Resource Management
Daily Review
Journaling
Automation
```

Domain không đồng nghĩa với database.

Ví dụ:

```text
Task
```

là một khái niệm trong domain, dù bạn chưa biết nó sẽ được lưu bằng PostgreSQL, SQLite hay Google Tasks.

---

# 3. Domain Object / Domain Entity

**Domain Object** = một khái niệm mà hệ thống cần hiểu và thao tác.

Ví dụ:

```text
Task
CalendarEvent
DailySession
Mood
Project
Resource
Journal
```

Ví dụ `Task`:

```text
Task
├── title
├── deadline
├── priority
├── effort
├── status
└── resources
```

Đây mới là lúc bắt đầu suy nghĩ:

> “Task của hệ thống thực sự có những thuộc tính gì?”

---

# 4. Domain Model

**Domain Model** = mô hình hóa toàn bộ các domain object và quan hệ giữa chúng.

Ví dụ:

```text
Project
   │
   ├── Task
   │     │
   │     └── Resource
   │
   └── DailySession
          │
          ├── Mood
          ├── Task
          └── Journal
```

Domain Model trả lời:

> “Các khái niệm trong hệ thống liên hệ với nhau như thế nào?”

Nó chưa phải database schema.

---

# 5. Capability

**Capability** = khả năng mà sản phẩm cung cấp.

Ví dụ:

```text
Email
├── Read
├── Preview
└── Delete

Calendar
├── View today's schedule
├── Plan tasks
└── Review schedule

Resource
├── Open Google Drive file
├── Open local file
└── Preview resource
```

Capability nói:

> “Hệ thống có thể làm gì?”

Trong khi workflow nói:

> “Người dùng thực hiện những việc đó theo trình tự nào?”

---

# 6. Capability Map

**Capability Map** = bản đồ toàn bộ capabilities.

Ví dụ:

```text
Personal Workspace
│
├── Communication
│   └── Email
│
├── Planning
│   ├── Calendar
│   └── Task
│
├── Resource Management
│   ├── Google Drive
│   └── Local Files
│
└── Daily Review
    └── Journal
```

Nó giúp tránh tình trạng:

> “Nghĩ feature này hay quá → code ngay.”

Bạn nhìn được **toàn bộ phạm vi hệ thống trước khi implementation**.

---

# 7. Workflow

**Workflow** = chuỗi hành động để đạt một mục tiêu.

Workflow của bạn:

```text
Open Workspace
      ↓
View Dashboard
      ↓
Review Calendar
      ↓
Check Must-do
      ↓
Select Task
      ↓
Work
      ↓
Review
      ↓
Journal
      ↓
Prepare tomorrow
```

Workflow là một trong những artifact quan trọng nhất của dự án.

---

# 8. User Workflow Map

Là tập hợp các workflow thực tế của người dùng.

Ví dụ:

```text
Start of Day
During Work
End of Day
Open Paper
Process File
Review Email
Plan Tomorrow
```

Nó giúp bạn thiết kế application **theo hành vi thực tế**, thay vì theo API.

---

# 9. State

**State** = trạng thái hiện tại của một object.

Ví dụ Task:

```text
planned
available
in_progress
completed
skipped
rescheduled
```

Một task không chỉ “có tồn tại”.

Nó đang **ở một trạng thái nào đó**.

Ví dụ:

```text
Read Paper
status = in_progress
```

---

# 10. State Transition

**State Transition** = sự chuyển từ state này sang state khác.

Ví dụ:

```text
planned
   ↓
available
   ↓
in_progress
   ↓
completed
```

Hoặc:

```text
in_progress
     ↓
   skipped
     ↓
rescheduled
```

Đây là thứ bạn phải xác định trước khi code, bởi vì rất nhiều bug application thực chất là:

> “Không biết trong trường hợp này object được phép chuyển sang trạng thái nào.”

---

# 11. State Machine

**State Machine** = mô hình chính thức hóa các state + transition.

Ví dụ:

```text
                 ┌───────────┐
                 │  PLANNED  │
                 └─────┬─────┘
                       ↓
                 ┌───────────┐
                 │ AVAILABLE │
                 └─────┬─────┘
                       ↓
                ┌─────────────┐
                │ IN_PROGRESS │
                └──────┬──────┘
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
        COMPLETED             SKIPPED
                                  ↓
                             RESCHEDULED
```

State machine đặc biệt quan trọng đối với:

- Task
    
- Daily Session
    
- Automation
    
- Email processing
    
- File processing
    

---

# 12. Business Rule

**Business Rule** = quy tắc nghiệp vụ của application.

Ví dụ của bạn:

> Nếu mood = Low, ưu tiên các task có cognitive load thấp.

Đó là business rule.

Hoặc:

> Must-do không được tự động loại bỏ khi mood thay đổi.

Hoặc:

> Một task đã completed không xuất hiện trong danh sách task cần làm hôm nay.

Google API không quyết định những thứ này.

**Bạn quyết định.**

---

# 13. Source of Truth

**Source of Truth** = nơi chứa phiên bản dữ liệu được xem là chính thức.

Ví dụ:

```text
Calendar Event
→ Google Calendar = source of truth

Gmail Message
→ Gmail = source of truth

Drive File
→ Google Drive = source of truth
```

Nhưng:

```text
Mood
→ Your Application

DailySession
→ Your Application

Task recommendation
→ Your Application
```

Đây là một trong những khái niệm quan trọng nhất của dự án.

---

# 14. Application State

**Application State** = những thông tin mà **chính application của bạn cần nhớ**.

Ví dụ:

```text
current_daily_session
selected_mood
task_status
resource_links
last_processed_email
automation_status
```

Google Workspace không nhất thiết biết những thứ này.

Đây chính là lý do sau này có thể cần DB.

---

# 15. Metadata

**Metadata** = dữ liệu mô tả dữ liệu khác.

Ví dụ Google Drive có:

```text
file_id
name
mime_type
created_time
modified_time
```

Bạn có thể có metadata riêng:

```text
resource_id
resource_type
linked_task
display_name
open_mode
```

Ví dụ:

```text
paper.pdf
```

là resource.

Còn:

```text
linked_to = Task #123
open_mode = internal_viewer
```

là metadata của application.

---

# 16. Resource

Trong thiết kế của bạn, **Resource** = bất kỳ tài nguyên nào mà Task/Project có thể sử dụng.

Ví dụ:

```text
Google Drive file
Google Doc
Gmail thread
Calendar event
Local PDF
Local CSV
Local folder
```

Ta có thể abstraction chúng thành:

```text
Resource
├── provider
├── type
├── identifier
└── metadata
```

---

# 17. Abstraction

**Abstraction** = che giấu implementation cụ thể phía sau một interface chung.

Ví dụ UI chỉ biết:

```text
Open Resource
```

Nó không cần biết:

```text
if Google Drive:
    open browser

if local PDF:
    open Electron viewer

if local DOCX:
    open Word
```

Thay vào đó:

```text
Resource
    ↓
Resource Handler
    ↓
appropriate implementation
```

Đây là abstraction.

---

# 18. Adapter

**Adapter** = lớp chuyển đổi giữa application và một external system.

Ví dụ:

```text
Application
     ↓
Google Calendar Adapter
     ↓
Google Calendar API
```

hoặc:

```text
Application
     ↓
Local File Adapter
     ↓
Node.js filesystem
```

Application không cần biết chi tiết API bên ngoài.

Nó chỉ cần nói:

```text
calendar.getToday()
```

Adapter chịu trách nhiệm gọi Google API.

---

# 19. Integration Boundary / API Boundary

**Boundary** = ranh giới giữa hai phần hệ thống.

Ví dụ:

```text
Your Application
       │
       │ Google API boundary
       ↓
Google Workspace
```

Hoặc:

```text
TypeScript
    │
    │ service boundary
    ↓
Python
```

Điều này rất quan trọng vì bạn đang có **TypeScript + Python + Google + local filesystem**.

Nếu không xác định boundary, code rất dễ trở thành:

```text
TS gọi Python
Python gọi Google
Google trả về TS
TS tự xử lý filesystem
Python lại đọc DB
...
```

và architecture nhanh chóng rối.

---

# 20. Orchestration

**Orchestration** = điều phối nhiều component để hoàn thành một workflow.

Ví dụ:

```text
Get today's workspace
        ↓
Calendar API
        ↓
Get Tasks
        ↓
Get linked resources
        ↓
Get email
        ↓
Build Dashboard
```

Không một API nào tự làm tất cả.

Application của bạn **orchestrate** chúng.

Đây chính là một trong những vai trò chính của TypeScript backend/core.

---

# 21. Control Surface

Tôi dùng thuật ngữ này để mô tả Dashboard của bạn.

**Control Surface** = giao diện nơi người dùng quan sát trạng thái và điều khiển hệ thống.

Dashboard của bạn:

```text
Email
Calendar
Tasks
Resources
Mood
Journal
```

không nhất thiết sở hữu dữ liệu đó.

Nó là **nơi người dùng điều khiển workflow**.

Ví dụ:

```text
Google Calendar
      ↓
      │
Dashboard ←→ User
      │
      ↓
Task system
```

---

# 22. Application Shell

**Application Shell** = lớp bao quanh toàn bộ application.

Trong dự án của bạn:

> Electron chính là application shell.

Nó cung cấp:

- cửa sổ desktop
    
- filesystem access
    
- native OS integration
    
- notifications
    
- application lifecycle
    
- khả năng mở file bằng default application
    
- chứa UI TypeScript/React
    

Nó không nhất thiết chứa toàn bộ business logic.

---

# 23. Infrastructure

**Infrastructure** = các hệ thống nền tảng mà application dựa vào.

Trong dự án của bạn:

```text
Google Workspace
Local filesystem
Electron
Operating System
Python runtime
Database (nếu có)
```

là infrastructure.

Application của bạn nằm **trên** infrastructure đó.

---

# 24. Persistence

**Persistence** = khả năng giữ dữ liệu sau khi application đóng.

Ví dụ:

```text
Application đóng
↓
Mở lại
↓
Task vẫn còn
```

thì task đã được persist.

Persistence có thể dùng:

```text
JSON
SQLite
PostgreSQL
Google Sheets
Google Calendar
```

Không phải persistence lúc nào cũng = database.

---

# 25. Persistence Layer

**Persistence Layer** = phần application chịu trách nhiệm lưu/đọc application state.

Ví dụ:

```text
Task Service
     ↓
Persistence Layer
     ↓
SQLite
```

Nếu sau này đổi:

```text
SQLite → PostgreSQL
```

Task Service không nên phải viết lại toàn bộ.

---

# 26. Database Schema

**Schema** = cấu trúc dữ liệu trong database.

Ví dụ:

```text
tasks
----------------
id
title
status
deadline
priority
```

Nhưng **chưa nên thiết kế schema ở giai đoạn hiện tại**.

Bạn phải có:

```text
Workflow
↓
Domain Model
↓
State
↓
Persistence requirements
↓
Database schema
```

chứ không nên:

```text
PostgreSQL
↓
tạo 30 tables
↓
tìm xem cần dùng chúng vào đâu
```

---

# 27. Feature Boundary

**Feature Boundary** = xác định feature nào thuộc responsibility của phần nào.

Ví dụ:

```text
Google owns:
    Gmail message
    Calendar event
    Drive file

Your application owns:
    Mood
    Task recommendation
    Daily session
    Resource linking
```

Đây là **rất quan trọng** vì nó ngăn application của bạn “ôm” tất cả dữ liệu.

---

# 28. Extension

**Extension** = chức năng bổ sung có thể kết nối với core nhưng không phải core.

Ví dụ:

```text
Core Workspace
       │
       ├── Journal Extension
       ├── Obsidian Extension
       ├── Analytics Extension
       └── AI Extension
```

Journal/Obsidian của bạn rất phù hợp làm extension.

Core không nên phụ thuộc vào Obsidian.

---

# 29. Service

**Service** = một component chịu trách nhiệm cho một nhóm logic.

Ví dụ:

```text
CalendarService
EmailService
TaskService
ResourceService
JournalService
```

Ví dụ:

```text
CalendarService
├── getToday()
├── getTomorrow()
└── createEvent()
```

Service là cách tổ chức logic, **không nhất thiết là một server riêng**.

---

# 30. Python Service

Trong kiến trúc của bạn, Python có thể trở thành service riêng khi computation đủ phức tạp:

```text
TypeScript
    ↓
Python Service
    ↓
analysis
ML
document processing
scientific computing
```

Nhưng **không nên ép mọi thứ sang Python**.

TypeScript có thể xử lý orchestration/application logic.

Python phù hợp với computational workloads.

---

# 31. MVP

**MVP = Minimum Viable Product**.

Không phải:

> “phiên bản có ít feature nhất có thể.”

Mà là:

> **phiên bản nhỏ nhất có một vòng giá trị hoàn chỉnh.**

MVP của bạn có thể là:

```text
Open Workspace
      ↓
Today's Calendar
      ↓
Must-do
      ↓
Mood
      ↓
Select Task
      ↓
Open Resource
      ↓
Complete Task
      ↓
End-of-day Review
```

Nếu vòng này hoạt động tốt, bạn đã có một sản phẩm.

---

# 32. Artifact

**Artifact** = một sản phẩm trung gian được tạo ra trong quá trình thiết kế.

Ví dụ:

```text
product-definition.md
capability-map.md
workflow-map.md
domain-model.md
state-machine.md
architecture.md
```

Chúng không phải documentation viết cho đẹp.

Chúng là **công cụ tư duy và contract trước implementation**.

---

# II. Bây giờ áp dụng tất cả vào dự án của bạn

Ta có thể nhìn hệ thống như sau:

```text
                     PERSONAL WORKSPACE
                              │
                              ▼
                     ┌────────────────┐
                     │  Daily Session │
                     └───────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ↓              ↓              ↓
          Calendar          Task           Mood
              │              │              │
              │              └──────┬───────┘
              │                     ↓
              │               Task Selection
              │                     │
              └──────────────┬──────┘
                             ↓
                         Resources
                         /        \
                        /          \
                   Google          Local
                    Drive         Files
                      │              │
                      └──────┬───────┘
                             ↓
                           Work
                             ↓
                           Review
                             ↓
                          Journal
                             ↓
                     Tomorrow Planning
```

Và infrastructure:

```text
                  ELECTRON
                     │
              Application Core
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
     Google        Local       Python
     APIs          FS          Service
        │
 ┌──────┼───────────────┐
 ↓      ↓       ↓       ↓
Gmail Calendar Drive Sheets
```

---

# III. Điều gì thuộc Google và điều gì thuộc application?

Đây là bảng tôi muốn bạn **chốt lại trước khi code**:

|Thành phần|Owner|
|---|---|
|Gmail message|Google|
|Gmail thread|Google|
|Calendar event|Google|
|Drive file|Google|
|Google Doc|Google|
|Google Sheet|Google|
|Local file|OS / filesystem|
|Mood|**Application**|
|Task recommendation|**Application**|
|Daily Session|**Application**|
|Must-do classification|**Application**|
|Resource linking|**Application**|
|Task state|**Application**|
|End-of-day workflow|**Application**|
|Journal orchestration|**Application**|
|Python analysis|**Python service**|

Đây là **feature boundary + source-of-truth boundary**.

---

# IV. Chốt lại: trước khi code cần làm gì?

Tôi sẽ thu gọn toàn bộ những gì chúng ta đã nói thành **8 bước**.

## Phase 1 — Product

### 1. Product Definition

Viết:

```text
What is Personal Workspace?
What problem does it solve?
What is explicitly outside its scope?
```

**Output:**

```text
01-product-definition.md
```

---

## Phase 2 — Capability

### 2. Capability Map

Liệt kê:

```text
Email
Calendar
Task
Mood
Resource
Daily Review
Journal
```

và capabilities của từng domain.

**Output:**

```text
02-capability-map.md
```

---

## Phase 3 — Workflow

### 3. Core Workflow

Viết chính xác:

```text
Start of Day
During Day
End of Day
```

và các workflow phụ:

```text
Open Email
Open Resource
Complete Task
Reschedule Task
Review Day
```

**Output:**

```text
03-workflows.md
```

---

## Phase 4 — Domain

### 4. Domain Model

Chốt những object ban đầu:

```text
DailySession
Task
Mood
Schedule
Resource
Project
Journal
```

và quan hệ giữa chúng.

**Output:**

```text
04-domain-model.md
```

---

## Phase 5 — State

### 5. State Machines

Ít nhất xác định state cho:

```text
Task
DailySession
Resource processing
Automation
```

Ví dụ:

```text
Task:
planned
→ available
→ in_progress
→ completed

             ↘ skipped
                  ↓
             rescheduled
```

**Output:**

```text
05-state-transitions.md
```

---

## Phase 6 — Ownership

### 6. Feature Boundaries + Source of Truth

Chốt:

```text
Google owns what?
Application owns what?
Filesystem owns what?
Python owns what?
```

**Output:**

```text
06-system-boundaries.md
```

---

## Phase 7 — Architecture

### 7. Architecture

Sau khi 6 thứ trên ổn mới quyết định:

```text
Electron
TypeScript
Google API adapters
Local filesystem adapter
Python service
Persistence layer
```

Và vẽ:

```text
Electron
   ↓
Application Core
   ├── Google Adapter
   ├── Local Adapter
   ├── Task Engine
   ├── Daily Session
   └── Extension System
             ↓
       Python Service
```

**Output:**

```text
07-architecture.md
```

---

## Phase 8 — Persistence

### 8. Data Strategy

**Lúc này mới hỏi:**

> Có cần DB không?

Lập bảng:

```text
Object              Source of Truth
─────────────────────────────────────
Gmail               Google
Calendar            Google
Drive               Google
Task                Application
Mood                Application
DailySession        Application
ResourceLink        Application
Journal             Local/Extension
```

Sau đó mới quyết định:

```text
No persistence
      ↓
JSON
      ↓
SQLite
      ↓
PostgreSQL
```

**Output:**

```text
08-data-strategy.md
```

---

# V. Và sau 8 bước này mới bắt đầu code

Thứ tự cuối cùng sẽ là:

```text
                    DESIGN
                       │
                       ▼
              Product Definition
                       ↓
               Capability Map
                       ↓
                User Workflows
                       ↓
                 Domain Model
                       ↓
                State Machines
                       ↓
             System Boundaries
                       ↓
                  Architecture
                       ↓
                Data Strategy
                       │
                       ▼
                    CODE
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
       Electron     Google API    Python
       / TypeScript   adapters     service
```

### Có 4 thứ bạn **chưa cần làm**

**Chưa cần:**

- thiết kế database schema;
    
- viết Google API integration;
    
- viết Python service;
    
- thiết kế UI chi tiết.
    

Đặc biệt **đừng mở Figma rồi vẽ dashboard trước**. UI hiện tại chỉ nên được phác thảo đủ để kiểm chứng workflow. Nếu vẽ UI quá sớm, bạn rất dễ vô thức biến những quyết định UI thành quyết định architecture.

---

## Và đây là “definition of ready” của dự án

Tôi sẽ coi dự án **đủ điều kiện bắt đầu code** khi bạn có thể trả lời rõ 8 câu này:

1. **Application tồn tại để giải quyết vấn đề gì?**
    
2. **Nó có những capability nào?**
    
3. **Một ngày làm việc đi qua workflow nào?**
    
4. **Những domain object nào tồn tại?**
    
5. **Mỗi object có những state nào và chuyển state ra sao?**
    
6. **Google, filesystem và application mỗi bên sở hữu dữ liệu gì?**
    
7. **Các component TypeScript/Electron/Google/Python giao tiếp với nhau ở đâu?**
    
8. **Application thực sự cần persist những gì?**
    

Nếu 8 câu này rõ, **việc code gần như trở thành một bài toán implementation** thay vì tiếp tục thiết kế trong lúc code.

Với dự án của bạn, tôi sẽ **chốt core hiện tại tại đây**, không thêm feature nữa. Bước tiếp theo hợp lý nhất là tạo `01-product-definition.md` → `08-data-strategy.md` theo đúng thứ tự trên; sau mỗi artifact bạn kiểm tra và sửa, rồi mới đi tiếp.