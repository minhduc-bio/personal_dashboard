Để nghiệm thu Bảng điều khiển, bạn hãy mở Terminal lên và thực hiện bài kiểm tra tay (Manual Testing) toàn diện theo checklist dưới đây.

  

### 1. Kiểm tra Khởi động & File hệ thống

- [x] **Màn hình chính:** Ứng dụng có khởi động thành công, hiển thị đúng ngày hôm nay (2026-08-06) và trạng thái phiên mặc định là `Created` không?
    
      
    
- [x] **Thư mục tự tạo:** Nhìn sang thanh Explorer của trình soạn thảo, kiểm tra xem thư mục `data/` và `data/sessions/` đã tự động sinh ra chưa.
    
      
    

### 2. Kiểm tra Menu 1: Tích hợp Google Calendar

- [x] **Hiển thị lịch:** Gõ `1`. Danh sách sự kiện có hiện ra đúng như khi bạn test API độc lập trước đó không?
    
      
    
- [x] **Luồng điều hướng:** Nhấn Enter để xem hệ thống có quay về Bảng điều khiển chính một cách mượt mà (không bị văng khỏi chương trình) không.
    
      
    

### 3. Kiểm tra Menu 2 & 3: Quản lý Công việc (Task)

- [x] **Thêm Task (Đúng chuẩn):** Gõ `2`, tạo một công việc mới (VD: "Review code") và nhập mức năng lượng chuẩn (`High`, `Neutral`, hoặc `Low`).
    
      
    
- [x] **Bắt lỗi validation (Cố tình làm sai):** Gõ `2`, thử thêm một Task nhưng gõ mức năng lượng sai bậy bạ (VD: `Rất cao`). Hệ thống có in ra thông báo lỗi và từ chối lưu không?
    
      
    
- [x] **Hiển thị danh sách:** Gõ `3`. Các Task vừa tạo có xuất hiện đầy đủ kèm theo biểu tượng ⏳ và mức năng lượng tương ứng không?
    
      
    

### 4. Kiểm tra Menu 4: Vòng đời Phiên làm việc (Session)

- [x] **Cập nhật hợp lệ:** Gõ `4`, chuyển trạng thái phiên từ `Created` sang `Planning`. Kiểm tra trên đỉnh Bảng điều khiển xem trạng thái đã được cập nhật chưa.
    
      
    
- [x] **Bắt lỗi trạng thái:** Gõ `4`, thử nhập một trạng thái không có trong thiết kế (VD: `Sleeping`). Hệ thống có chặn lại và báo lỗi không?
    
      
    

### 5. Kiểm tra Tính bền vững của dữ liệu (Quan trọng nhất)

- [ ] **Thoát an toàn:** Gõ `0` để đóng chương trình.
    
      
    
- [ ] **Kiểm tra File:** Mở thử file `data/tasks.json` và `data/sessions/2026-08-06.json` xem dữ liệu bạn vừa nhập có thực sự được lưu vào trong đó chưa.
    
      
    
- [ ] **Reload hệ thống:** Chạy lại lệnh `python -m src.main`. Số lượng Task và trạng thái `Planning` có được giữ nguyên như trước khi thoát không?
    
      
    

Quá trình test các tính năng này của bạn đang diễn ra như thế nào rồi?