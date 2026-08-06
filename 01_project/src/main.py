import os
import uuid
from datetime import datetime

# Import các hàm từ module chúng ta đã viết
from src.storage import init_storage, load_tasks, save_tasks, load_session, save_session
from src.models import Task, Session

def clear_screen():
    """Xóa màn hình Terminal cho gọn gàng."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    # 1. Khởi tạo hệ thống lưu trữ
    init_storage()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 2. Tải hoặc tạo Session của ngày hôm nay
    session = load_session(today_str)
    if not session:
        session = Session(date=today_str, state="Created")
        save_session(session)

    # 3. Tải danh sách công việc
    tasks = load_tasks()

    # 4. Vòng lặp giao diện chính (Bảng điều khiển)
    while True:
        clear_screen()
        print(f"=== BẢNG ĐIỀU KHIỂN v0 ({today_str}) ===")
        print(f"Trạng thái phiên: {session.state}")
        print(f"Tổng số Task hiện có: {len(tasks)}")
        print("-" * 40)
        print("1. Xem lịch Google Calendar sắp tới")
        print("2. Thêm công việc mới (Task)")
        print("3. Xem danh sách công việc")
        print("4. Cập nhật trạng thái phiên làm việc")
        print("0. Lưu & Thoát")
        print("-" * 40)
        
        choice = input("Chọn thao tác (0-4): ")

        if choice == "1":
            clear_screen()
            print("--- LỊCH GOOGLE CALENDAR ---")
            # Gọi trực tiếp script đã test thành công ở Giai đoạn 3
            os.system("python src/calendar_client.py")
            input("\nNhấn Enter để quay lại Dashboard...")

        elif choice == "2":
            clear_screen()
            print("--- THÊM CÔNG VIỆC MỚI ---")
            title = input("Nhập tên công việc: ")
            mood = input("Mức năng lượng yêu cầu (High/Neutral/Low): ").capitalize()
            
            if mood in ["High", "Neutral", "Low"]:
                new_task = Task(
                    id=str(uuid.uuid4())[:6], # Tạo ID ngẫu nhiên 6 ký tự
                    title=title,
                    mood_affinity=mood,
                    status="pending",
                    created_at=today_str
                )
                tasks.append(new_task)
                save_tasks(tasks)
                print("✅ Đã thêm công việc thành công!")
            else:
                print("❌ Mức năng lượng không hợp lệ. Vui lòng nhập đúng High, Neutral hoặc Low.")
            input("\nNhấn Enter để quay lại Dashboard...")

        elif choice == "3":
            clear_screen()
            print("--- DANH SÁCH CÔNG VIỆC ---")
            if not tasks:
                print("Chưa có công việc nào.")
            else:
                for t in tasks:
                    status_icon = "✅" if t.status == "done" else "⏳"
                    print(f"[{t.id}] {status_icon} {t.title} (Năng lượng: {t.mood_affinity})")
            input("\nNhấn Enter để quay lại Dashboard...")

        elif choice == "4":
            clear_screen()
            print("--- CHUYỂN TRẠNG THÁI PHIÊN ---")
            print(f"Trạng thái hiện tại: {session.state}")
            print("Các trạng thái hợp lệ: Created -> Planning -> Active -> Reviewing -> Closed")
            new_state = input("Nhập trạng thái mới: ").capitalize()
            
            if new_state in ["Created", "Planning", "Active", "Reviewing", "Closed"]:
                session.state = new_state
                save_session(session)
                print(f"✅ Đã cập nhật trạng thái thành: {new_state}")
            else:
                print("❌ Trạng thái không hợp lệ theo Schema.")
            input("\nNhấn Enter để quay lại Dashboard...")

        elif choice == "0":
            print("Đang lưu dữ liệu... Tạm biệt!")
            break
        
        else:
            print("Lựa chọn không hợp lệ!")
            input("\nNhấn Enter để thử lại...")

if __name__ == "__main__":
    main()