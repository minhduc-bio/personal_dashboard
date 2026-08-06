import os
from src.storage import init_storage, load_tasks, save_tasks, load_session, save_session
from datetime import date
def clear_screen():
    # Tùy chọn làm sạch Terminal để UI gọn gàng (có thể bỏ qua nếu muốn xem log cũ)
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    init_storage()
    tasks = load_tasks()
    today_str = date.today().isoformat()
    session = load_session()

    # Khai báo vòng đời chuẩn để kiểm soát State Machine
    STATE_FLOW = ["Created", "Planning", "Active", "Reviewing", "Closed"]

    while True:
        print("\n" + "="*45)
        print(f"BẢNG ĐIỀU KHIỂN - {session.date}")
        print(f"Trạng thái phiên: [{session.state}]")
        print("="*45)
        print("1. Xem lịch Google Calendar")
        print("2. Thêm công việc mới (Task)")
        print("3. Xem danh sách công việc")
        print("4. Đánh dấu hoàn thành công việc (Update!)")
        print("5. Chuyển trạng thái Phiên (Update!)")
        print("0. Thoát và Lưu")
        
        choice = input("\nChọn chức năng (0-5): ").strip()
        
        if choice == '0':
            print("Đã lưu dữ liệu. Tạm biệt!")
            break
            
        elif choice == '1':
            print("\n[Tích hợp Google Calendar sẽ được gọi ở đây]")
            
        elif choice == '2':
            # FIX BUG 1 & 4: Vòng lặp bắt lỗi rỗng và Thêm tùy chọn Hủy
            while True:
                title = input("\nNhập tên công việc (hoặc gõ '0' để Hủy): ").strip()
                if title == '0':
                    print("Đã hủy thêm công việc.")
                    break
                if not title:
                    print("Lỗi: Tên công việc không được để trống!")
                    continue
                
                # FIX BUG 2: Chuẩn hóa khoảng trắng và viết hoa chữ đầu
                energy = input("Mức năng lượng (High/Neutral/Low): ").strip().capitalize()
                if energy not in ["High", "Neutral", "Low"]:
                    print("Lỗi: Mức năng lượng không hợp lệ. Vui lòng nhập đúng High, Neutral hoặc Low.")
                    continue
                    
                # Khởi tạo Task (Pydantic models cần được import)
                from src.models import Task
                new_task = Task(title=title, energy_level=energy)
                tasks.append(new_task)
                save_tasks(tasks)
                print(f"-> Đã thêm thành công: '{title}' (⚡ {energy})")
                break

        elif choice == '3':
            print("\n--- DANH SÁCH CÔNG VIỆC ---")
            if not tasks:
                print("Chưa có công việc nào.")
            else:
                for i, t in enumerate(tasks):
                    status_icon = "✅" if t.status == "done" else "⏳"
                    print(f"{i+1}. [{status_icon}] {t.title} (Năng lượng: {t.energy_level})")
                    
        elif choice == '4':
            # FIX BUG 3: Bổ sung tính năng đánh dấu hoàn thành
            pending_tasks = [(i, t) for i, t in enumerate(tasks) if t.status == 'pending']
            
            if not pending_tasks:
                print("\nKhông có công việc nào đang chờ xử lý.")
                continue
                
            print("\n--- HOÀN THÀNH CÔNG VIỆC ---")
            for idx, (original_idx, t) in enumerate(pending_tasks):
                print(f"{idx + 1}. {t.title} (⚡ {t.energy_level})")
            
            try:
                task_choice = input(f"\nChọn STT công việc đã xong (1-{len(pending_tasks)}, hoặc '0' để Hủy): ").strip()
                if task_choice == '0':
                    continue
                
                selected_idx = int(task_choice) - 1
                if 0 <= selected_idx < len(pending_tasks):
                    real_idx = pending_tasks[selected_idx][0]
                    tasks[real_idx].status = 'done'
                    save_tasks(tasks)
                    print(f"-> Tuyệt vời! Đã hoàn thành: '{tasks[real_idx].title}' 🎉")
                else:
                    print("Lỗi: Số thứ tự không hợp lệ.")
            except ValueError:
                print("Lỗi: Vui lòng nhập một con số.")

        elif choice == '5':
            # FIX BUG 5 & 6: Khóa logic vòng đời và chuyển sang chọn số
            current_idx = STATE_FLOW.index(session.state)
            if current_idx == len(STATE_FLOW) - 1:
                print("\nPhiên của bạn đã ở trạng thái cuối ngày (Closed). Không thể tiến xa hơn.")
                continue
                
            print("\n--- CẬP NHẬT TRẠNG THÁI ---")
            print(f"Trạng thái hiện tại: [{session.state}]")
            print("Các bước tiếp theo có thể chuyển:")
            
            # Chỉ cho phép tiến tới các trạng thái tiếp theo, không cho lùi lại
            next_states = STATE_FLOW[current_idx+1:]
            for i, state in enumerate(next_states):
                print(f"{i + 1}. -> {state}")
                
            try:
                state_choice = input(f"\nChọn trạng thái tiếp theo (1-{len(next_states)}, hoặc '0' để Hủy): ").strip()
                if state_choice == '0':
                    continue
                    
                selected_idx = int(state_choice) - 1
                if 0 <= selected_idx < len(next_states):
                    session.state = next_states[selected_idx]
                    save_session(session)
                    print(f"-> Đã chuyển Phiên sang trạng thái: [{session.state}]")
                else:
                    print("Lỗi: Lựa chọn không hợp lệ.")
            except ValueError:
                print("Lỗi: Vui lòng nhập một con số.")

        else:
            print("Lỗi: Menu không tồn tại. Vui lòng nhập số từ 0-5.")

if __name__ == "__main__":
    main()