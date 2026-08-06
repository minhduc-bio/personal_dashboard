## Core Workflow:
- Start of Day -> During Day -> End of Day
- Trong đó, mỗi một core có những workflow phụ sau
	1. Start of day
		- Open Workspace
		- Dialog: Hôm nay bạn cảm thấy thế nào: High/Neutral/Low mood
		- Mở hộp thư mail: Đọc trên workspace/Direct về Gmail để đọc. (*optional: có thể xóa các gmail rác nếu người dùng muốn, feature này có thể phát triển từ script python đã có sẵn Gmail API*)
		- Trở về UI chính của Workspace
		- Lựa chọn Calendar -> giao diện Calendar
		- Open Today/This week/This month Calendar (setup từ trước - có thể setup ngay trên UI hoặc setup trên Google Calendar) -> bao gồm những fixed schedule (deadline, homework, remind daily/weekly)
		- Bên trong Calendar có một mục phụ thuộc vào lựa chọn Dialog -> gợi ý các thẻ có đúng thuộc tính mood -> kéo thả để thêm task/schedule. Hoặc tự generate thẻ theo thuộc tính mood. Để thêm vào lịch
	2. During Day:
		- File storage (Google Drive/Local Storage) là feature sử dụng chính. Chọn file để có thể mở trực tiếp trên UI/Direct về web của các tiện ích Google Workspace. 