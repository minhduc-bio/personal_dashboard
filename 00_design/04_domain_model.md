# Domain Model — Personal Workspace v0.1

## 1. Domain Overview

Personal Workspace là một **personal work orchestration environment** nằm trên ba nhóm infrastructure:

1. **Google Workspace**
    
    - Gmail
        
    - Calendar
        
    - Drive
        
    - Docs
        
    - Sheets
        
    - Tasks
        
    - Các Google Workspace services khác khi cần
        
2. **Local Environment**
    
    - Local filesystem
        
    - Markdown notes
        
    - OneNote
        
    - Local applications
        
    - Local datasets/files
        
3. **Application Services**
    
    - Task recommendation
        
    - Mood-based planning
        
    - Resource linking
        
    - File organization
        
    - Daily review
        
    - Planning
        
    - Sandbox management
        
    - Pomodoro
        
    - Terminal / execution tools
        
    - Data collection
        

Google Workspace và local filesystem là nơi chứa dữ liệu gốc của nhiều resource. Personal Workspace chủ yếu quản lý **workflow, state, relationship và orchestration** giữa các resource đó.

---

# 2. Core Domain

Core domain của hệ thống được tổ chức quanh một chu kỳ:

```text
Daily Session
      │
      ├── Start of Day
      │      ├── Mood
      │      ├── Calendar
      │      └── Task Planning
      │
      ├── During Day
      │      ├── Task Execution
      │      ├── Resource Access
      │      ├── Note Taking
      │      └── Sandbox
      │
      └── End of Day
             ├── Completion
             ├── Daily Review
             ├── Knowledge Review
             └── Replanning
```

Core domain entities:

```text
DailySession
Mood
Schedule
Task
Resource
Note
DailyReview
```

Supporting entities:

```text
Project
Workspace
Sandbox
TerminalSession
PomodoroSession
```

External resources:

```text
GoogleResource
LocalResource
```

---

# 3. Workspace

## Workspace

`Workspace` là application-level container đại diện cho toàn bộ môi trường làm việc cá nhân.

```text
Workspace
├── Projects
├── DailySessions
├── Resources
├── Notes
├── Sandbox
└── Configuration
```

### Responsibility

Workspace chịu trách nhiệm:

- khởi tạo application;
    
- xác định các local workspace paths;
    
- kết nối các Google Workspace services;
    
- cung cấp context cho Daily Session;
    
- quản lý navigation giữa các domain;
    
- cung cấp application-level configuration.
    

Workspace **không sở hữu dữ liệu gốc của Google Workspace**.

---

# 4. DailySession

## DailySession

`DailySession` là entity trung tâm của core workflow.

Một DailySession đại diện cho **một chu kỳ làm việc trong một ngày**.

```text
DailySession
├── date
├── mood
├── schedule
├── tasks
├── resources
├── notes
├── daily_review
└── planning_state
```

### Lifecycle

```text
Created
   ↓
Planning
   ↓
Active
   ↓
Reviewing
   ↓
Closed
```

### Responsibility

DailySession quản lý:

- trạng thái ngày hiện tại;
    
- mood đầu ngày;
    
- schedule;
    
- task được planned;
    
- task completion;
    
- resource được sử dụng;
    
- notes phát sinh;
    
- daily review;
    
- planning cho ngày tiếp theo.
    

DailySession **không sở hữu Calendar Event gốc**.

---

# 5. Mood

## Mood

`Mood` biểu diễn trạng thái người dùng tại thời điểm bắt đầu ngày.

MVP:

```text
High
Neutral
Low
```

Mood là **application state**, không phải Google Workspace resource.

### Responsibility

Mood cung cấp input cho:

```text
Mood
  ↓
Task Recommendation
  ↓
Task Candidates
  ↓
User Selection
  ↓
Schedule
```

Mood **không trực tiếp quyết định task phải làm**.

Nó chỉ là một input cho recommendation/planning system.

---

# 6. Schedule

## Schedule

`Schedule` đại diện cho cấu trúc thời gian của một DailySession.

Nó có thể bao gồm:

```text
Schedule
├── FixedSchedule[]
└── FlexibleSchedule[]
```

### Fixed Schedule

Được lấy từ Google Calendar hoặc các nguồn lịch đã được cấu hình:

- deadline;
    
- homework;
    
- reminder;
    
- recurring schedule;
    
- meeting;
    
- class;
    
- fixed appointment.
    

### Flexible Schedule

Được tạo hoặc điều chỉnh bởi Personal Workspace:

- task được kéo vào Calendar;
    
- task được generate dựa trên Mood;
    
- task được reschedule;
    
- study block;
    
- work block.
    

### Quan hệ

```text
DailySession
      │
      └── Schedule
             ├── FixedSchedule
             │       └── Google Calendar Event
             │
             └── FlexibleSchedule
                     └── Task
```

Điểm quan trọng:

> `Schedule` là application abstraction; `Google Calendar Event` là external resource.

---

# 7. Task

## Task

`Task` là đơn vị hành động mà người dùng cần thực hiện.

Ví dụ:

```text
Read paper
Complete homework
Analyze dataset
Review knowledge
Write notes
Organize files
```

### Suggested attributes

```text
Task
├── id
├── title
├── description
├── status
├── priority
├── deadline
├── estimated_duration
├── cognitive_load
├── mood_affinity
└── resources
```

### State

```text
Planned
   ↓
Available
   ↓
In Progress
   ↓
Completed

Available
   ↓
Skipped
   ↓
Rescheduled
```

### Mood relationship

Task có thể có:

```text
mood_affinity
```

Ví dụ:

```text
Task A → Low / Neutral
Task B → Neutral
Task C → High
```

Nhưng:

```text
Mood ≠ Task assignment
```

Mood chỉ tạo ra candidate list:

```text
Current Mood
     ↓
Task Recommendation
     ↓
Candidate Tasks
     ↓
User chooses
     ↓
Schedule
```

Người dùng vẫn là người quyết định.

---

# 8. Resource

## Resource

`Resource` là abstraction chung cho mọi tài nguyên được sử dụng trong quá trình thực hiện Task.

```text
Resource
├── GoogleResource
└── LocalResource
```

Ví dụ:

```text
GoogleResource
├── Drive File
├── Google Doc
├── Google Sheet
├── Gmail Thread
└── Calendar Event

LocalResource
├── PDF
├── Markdown
├── CSV
├── Image
├── Folder
└── OneNote resource
```

### Resource abstraction

```text
Resource
├── provider
├── resource_type
├── identifier
├── display_name
└── open_strategy
```

Ví dụ:

```text
provider = google_drive
resource_type = file
identifier = <Google Drive File ID>
```

hoặc:

```text
provider = local
resource_type = file
identifier = D:\Research\paper.pdf
```

---

# 9. ResourceLink

## ResourceLink

`ResourceLink` biểu diễn quan hệ giữa application entity và resource.

Ví dụ:

```text
Task
  │
  ├── ResourceLink → paper.pdf
  ├── ResourceLink → Google Doc
  └── ResourceLink → dataset.csv
```

ResourceLink rất quan trọng vì:

> File không nhất thiết thuộc Task; Task chỉ **tham chiếu** đến file.

### Suggested model

```text
ResourceLink
├── source_entity
├── resource
├── relationship_type
└── access_mode
```

Ví dụ:

```text
Task
  │
  └── ResourceLink
        │
        ├── resource = paper.pdf
        └── relationship = reference
```

---

# 10. Note

## Note

`Note` đại diện cho knowledge artifact được tạo trong quá trình học/làm việc.

MVP có thể hỗ trợ:

```text
Markdown Note
OneNote Note
```

### Note lifecycle

```text
Created
   ↓
Editing
   ↓
Sandboxed
   ↓
Reviewed
   ↓
Persisted
```

Note có thể liên kết với:

```text
Task
Project
Resource
DailySession
```

Ví dụ:

```text
DailySession
   │
   └── Task: Read Paper
          │
          ├── Resource: paper.pdf
          └── Note: paper-notes.md
```

---

# 11. Sandbox

## Sandbox

`Sandbox` là temporary workspace cho dữ liệu phát sinh trong quá trình làm việc.

Ví dụ:

```text
Sandbox
├── temporary notes
├── temporary files
├── intermediate outputs
└── unfinished work
```

Mục đích:

> Cho phép người dùng làm việc mà chưa phải quyết định ngay nơi lưu trữ lâu dài.

Cuối ngày:

```text
Sandbox
   ↓
Review
   ↓
Organize
   ↓
Persist
   ├── Google Drive
   └── Local filesystem
```

Sandbox vì vậy là một **application-managed temporary state**, không phải source of truth lâu dài.

---

# 12. DailyReview

## DailyReview

`DailyReview` đại diện cho quá trình kết thúc một DailySession.

MVP:

```text
DailyReview
├── mood
├── stress
├── achievements
├── completed_tasks
├── incomplete_tasks
└── planning_notes
```

### Lifecycle

```text
DailySession
     ↓
End of Day
     ↓
DailyReview
     ↓
Replanning
     ↓
Next DailySession
```

---

# 13. Daily Metrics

Các giá trị:

```text
Mood
Stress
Achievements
```

có thể được xem là **Daily Metrics**.

Ví dụ:

```text
2026-08-06
mood = Neutral
stress = 3
achievement = 4
```

Dữ liệu này có thể được export:

```text
DailyReview
      ↓
CSV
      ↓
Statistical analysis
      ↓
R / Python
```

Đây là một domain boundary rất tốt vì application có thể thu thập dữ liệu mà không cần ngay lập tức xây analytics engine.

---

# 14. Project

## Project

`Project` là một context lớn hơn Task.

Ví dụ:

```text
Project: R4DS Learning
```

có:

```text
Tasks
Resources
Notes
DailySessions
```

Quan hệ:

```text
Project
├── Tasks[]
├── Resources[]
└── Notes[]
```

Task có thể xuất hiện trong nhiều DailySession khác nhau:

```text
Project
   │
   └── Task
         │
         ├── DailySession 01
         ├── DailySession 02
         └── DailySession 03
```

Project là application entity.

---

# 15. PomodoroSession

## PomodoroSession

Đại diện cho một phiên tập trung.

```text
PomodoroSession
├── task
├── start_time
├── end_time
├── duration
└── status
```

Lifecycle:

```text
Created
 ↓
Running
 ↓
Paused
 ↓
Completed
```

Pomodoro là **supporting domain**, không phải core domain.

Nó phục vụ Task Execution.

---

# 16. TerminalSession

Nếu thêm Embedded Terminal:

```text
TerminalSession
├── shell
├── working_directory
├── started_at
└── status
```

Ví dụ:

```text
Task
  │
  └── TerminalSession
          │
          └── working_directory
              D:\Research\R4DS
```

TerminalSession là **runtime object**, không nhất thiết phải persist trong MVP.

---

# 17. External Resource Model

Các resource này **không thuộc sở hữu của Personal Workspace**:

```text
Google Workspace
│
├── Gmail
│   ├── Message
│   └── Thread
│
├── Calendar
│   ├── Calendar
│   └── Event
│
├── Drive
│   └── File
│
├── Docs
│   └── Document
│
├── Sheets
│   └── Spreadsheet
│
└── Tasks
    └── Task
```

Personal Workspace chỉ tạo **reference/relationship** đến chúng.

Ví dụ:

```text
Personal Task
      │
      └── ResourceLink
              │
              └── Google Drive File ID
```

Google Drive vẫn là source of truth.

---

# 18. Domain Relationships

## Core relationship

```text
Workspace
   │
   └── DailySession
          │
          ├── Mood
          │
          ├── Schedule
          │     ├── FixedSchedule
          │     │      └── Google Calendar Event
          │     │
          │     └── FlexibleSchedule
          │            └── Task
          │
          ├── Task[]
          │     │
          │     ├── ResourceLink[]
          │     │
          │     └── Note[]
          │
          ├── Sandbox
          │
          └── DailyReview
```

---

# 19. Project Relationship

```text
Project
│
├── Task[]
│    │
│    ├── ResourceLink[]
│    └── Note[]
│
├── ResourceLink[]
│
└── Note[]
```

Một Task có thể được đưa vào nhiều DailySession:

```text
Project
   │
   └── Task
        │
        ├── DailySession A
        ├── DailySession B
        └── DailySession C
```

---

# 20. Complete Domain Model

```text
                              WORKSPACE
                                  │
                     ┌────────────┴────────────┐
                     │                         │
                  PROJECT                 DAILY SESSION
                     │                         │
              ┌──────┼──────┐          ┌──────┼──────────────┐
              │      │      │          │      │              │
            TASK  RESOURCE NOTE       MOOD  SCHEDULE       SANDBOX
              │             │                 │
              │             │          ┌──────┴──────┐
              │             │          │             │
              │             │       FIXED        FLEXIBLE
              │             │          │             │
              │             │          ↓             ↓
              │             │    Google Event      TASK
              │             │
              ├─────────────┘
              │
              ↓
        RESOURCE LINK
              │
       ┌──────┴──────┐
       ↓             ↓
    GOOGLE         LOCAL
    RESOURCE      RESOURCE
       │             │
       ├─ Drive      ├─ PDF
       ├─ Gmail      ├─ CSV
       ├─ Docs       ├─ MD
       ├─ Sheets     ├─ Image
       └─ Calendar   └─ Folder

DAILY SESSION
      │
      └── DAILY REVIEW
             │
             ├── Mood
             ├── Stress
             ├── Achievements
             └── Replanning
```

---

# 21. Ownership / Source of Truth

|Domain Object|Owner|
|---|---|
|Workspace configuration|Application|
|DailySession|Application|
|Mood|Application|
|Task|Application|
|Schedule abstraction|Application|
|ResourceLink|Application|
|Project|Application|
|Note metadata|Application / Local|
|Sandbox|Application|
|DailyReview|Application|
|PomodoroSession|Application|
|TerminalSession|Runtime|
|Gmail Message|Google|
|Gmail Thread|Google|
|Calendar Event|Google|
|Drive File|Google|
|Google Doc|Google|
|Google Sheet|Google|
|Google Task|Google|
|Local file content|Local filesystem|
|OneNote content|OneNote|

---

# 22. Core Domain vs Supporting Domain

## Core Domain

Đây là phần tạo ra giá trị đặc thù của Personal Workspace:

```text
DailySession
Task Planning
Mood-based Recommendation
Resource Linking
Sandbox → Persistence
Daily Review
Replanning
```

## Supporting Domain

```text
Project
Note
Pomodoro
Terminal
Journal
```

## External Systems

```text
Gmail
Calendar
Drive
Docs
Sheets
Tasks
OneNote
Local filesystem
```

---

# 23. Một nguyên tắc kiến trúc quan trọng

Personal Workspace **không phải Google Workspace clone**.

Nó không sở hữu:

```text
Email UI
Google Docs editor
Google Sheets editor
Google Calendar engine
Google Drive storage
```

Thay vào đó:

```text
Google Workspace
        ↓
    API / Link
        ↓
Personal Workspace
        ↓
Planning / Navigation / Orchestration
        ↓
Google Workspace hoặc Local Application
```

Ví dụ:

```text
User sees email
      ↓
Personal Workspace
      ↓
Preview
      ↓
[Read]
      ↓
Gmail
```

Hoặc:

```text
Task
 ↓
ResourceLink
 ↓
Google Drive File
 ↓
[Open]
 ↓
Google Drive / internal viewer
```

Như vậy application giữ được **workflow continuity** mà không phải tái tạo những application đã rất hoàn thiện.

---

# 24. Domain Model Boundary

### Personal Workspace owns

```text
Planning
Task relationship
Mood
Daily Session
Resource relationship
Sandbox
Review
Replanning
```

### Google owns

```text
Communication
Calendar data
Cloud storage
Documents
Spreadsheets
Google Tasks
```

### Local environment owns

```text
Local files
Local applications
OneNote
Persistent Markdown vault
```

### External processing services own

```text
Data processing
ML
Scientific computation
Automation workers
```

---

# 25. Domain Model v0.1 — Minimal Entity Set

Nếu cần **đóng băng scope** để tiếp tục thiết kế architecture, tôi sẽ chỉ coi 9 object sau là chính thức ở v0.1:

```text
1. Workspace
2. Project
3. DailySession
4. Mood
5. Schedule
6. Task
7. Resource
8. ResourceLink
9. DailyReview
```

Các object sau để **supporting / optional**:

```text
Note
Sandbox
PomodoroSession
TerminalSession
Journal
```

Còn:

```text
Gmail
Calendar
Drive
Docs
Sheets
Tasks
OneNote
```

được coi là **external resources/services**, không phải core domain entities của Personal Workspace.