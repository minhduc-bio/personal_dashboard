
## Purpose

- Một môi trường làm việc cá nhân thống nhất,
- Sử dụng Google Workspace làm infrastructure chính.

## Problem

Hiện tại dữ liệu và workflow nằm rải rác:
- Google Calendar (sử dụng để lên plan và tạo lịch trình cho những công việc cố đinh )
- Google Drive (store file remote)
- Google Docs (bài tập, ý tưởng)
- Google Sheets (template đã sẵn sàng dành cho công việc)
- Gmail
- Google Tasks

Mục tiêu là tạo một lớp orchestration phía trên các dịch vụ này.

## Core principle

Google Workspace là source of truth cho dữ liệu gốc.

Application chỉ quản lý:
- write file (tạo dropbox để có thể nạp file trực tiếp vào google drive, thêm lịch trình trực tiếp trên dashboard thay vì nhập trên google calendar) (các feature khác thêm sau)
- workflow
- metadata
- automation
- application state