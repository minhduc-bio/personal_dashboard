1. Mở workspace
2. Dashboard hiện lên bao gồm:
	1. Email mới
		1. Đọc (direct to gmail.com)
		2. Đọc (có thể đọc trực tiếp mail trên dashboard)
		3. Xóa (đã có script xóa mail nhờ API key trên CLI)
	2. Calendar (cỡ lớn)
		1. Get today calendar -> Sử dụng lịch trình đã nhập từ hôm trước cho ngày hôm nay (công việc fixed) -> must-do (deadlines, homework,...)
		2. Mood selection: Low - Medium - High -> specify mỗi loại mood sẽ có những task phù hợp. User có thể kéo thả những Task này vào giao diện -> Task phụ bên cạnh must-do
	3. File storage: Google Drive/Local
		1. Google Drive: Quá khứ user sẽ note link các file cần sử dụng của must-do hoặc task vào trong calendar, khi get today calendar active -> panel sẽ hiện thị block file (link) direct to google drive / hoặc xem bằng một tab/panel/UI/application con bên trong dashboard.
		2. Local file: Tương tự, có cơ chế gắn file local với lịch -> mở file bằng default app/mở bằng  tab/panel/UI/application con trong dashboard. 
	4. End of the day:
		1. Cuối ngày, thông báo kiểm tra lịch trình, viết journal/đặt lại trạng thái của bản thân. (có thể thêm một extensions viết md và mở một vault tại folder này).