import os
from src.storage import (
    init_storage,
    load_tasks,
    save_tasks,
    save_session,
    get_or_create_today_session
)
from src.models import Task, SESSION_STATE_FLOW
from src.calendar_client import get_today_schedule


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def advance_state(session, target_state: str):
    """Tiến state của session ngầm theo hành động, không cho phép lùi."""
    current_idx = SESSION_STATE_FLOW.index(session.state)
    target_idx = SESSION_STATE_FLOW.index(target_state)
    
    if target_idx > current_idx:
        session.state = target_state
        save_session(session)


def main():
    init_storage()
    tasks = load_tasks()
    
    # Sửa lỗi crash ngày đầu tiên bằng cách dùng helper mới từ storage.py
    session = get_or_create_today_session()

    # Bổ sung Mood dialog đầu ngày nếu session chưa có mood
    if session.mood is None:
        print(f"\n--- CHÀO BUỔI SÁNG ({session.date}) ---")
        while True:
            mood_input = input("Hôm nay bạn cảm thấy thế nào? (High/Neutral/Low): ").strip().capitalize()
            if mood_input in ["High", "Neutral", "Low"]:
                session.mood = mood_input
                save_session(session)
                print(f"Đã ghi nhận trạng thái: {session.mood}")
                break
            else:
                print("Lỗi: Vui lòng nhập High, Neutral hoặc Low.")

    while True:
        print("\n" + "="*45)
        print(f"BẢNG ĐIỀU KHIỂN - {session.date}")
        print(f"Trạng thái phiên: [{session.state}] | Năng lượng: {session.mood}")
        print("="*45)
        print("1. Xem lịch Google Calendar (Update!)")
        print("2. Thêm công việc mới (Task)")
        print("3. Xem danh sách công việc (có lọc theo Mood)")
        print("4. Đánh dấu hoàn thành công việc")
        print("0. Kết thúc ngày và Lưu (Thoát)")
        
        choice = input("\nChọn chức năng (0-4): ").strip()
        
        if choice == '0':
            # Hành động thoát/kết ngày tự động chuyển state sang Closed
            advance_state(session, "Closed")
            print("Đã lưu dữ liệu. Tạm biệt!")
            break
            
        elif choice == '1':
            print("\n--- LỊCH HÔM NAY (Google Calendar) ---")
            try:
                # Tích hợp thật với calendar_client.py
                schedule = get_today_schedule()
                if not schedule:
                    print("Không có sự kiện nào trong ngày hôm nay.")
                else:
                    for e in schedule:
                        print(f"{e['start']} - {e['end']} | {e['summary']}")
            except Exception as e:
                print(f"Lỗi khi tải lịch: {e}")
                
            # Hành động xem lịch tự động đẩy trạng thái lên Planning
            advance_state(session, "Planning")
            
        elif choice == '2':
            while True:
                title = input("\nNhập tên công việc (hoặc gõ '0' để Hủy): ").strip()
                if title == '0':
                    print("Đã hủy thêm công việc.")
                    break
                if not title:
                    print("Lỗi: Tên công việc không được để trống!")
                    continue
                
                mood = input("Mức năng lượng yêu cầu (High/Neutral/Low): ").strip().capitalize()
                if mood not in ["High", "Neutral", "Low"]:
                    print("Lỗi: Mức năng lượng không hợp lệ. Vui lòng nhập đúng High, Neutral hoặc Low.")
                    continue
                    
                # Fix lỗi Pydantic: Đổi energy_level thành mood_affinity, bỏ id/created_at để dùng default factory
                new_task = Task(title=title, mood_affinity=mood)
                tasks.append(new_task)
                
                # Cập nhật ID task vào Session
                session.task_ids.append(new_task.id)
                
                save_tasks(tasks)
                save_session(session)
                print(f"-> Đã thêm thành công: '{title}' (⚡ {mood})")
                
                # Thêm Task đẩy trạng thái lên Planning (nếu đang ở Created)
                advance_state(session, "Planning")
                break

        elif choice == '3':
            print("\n--- DANH SÁCH CÔNG VIỆC ---")
            # Tính năng lọc Task theo mood_affinity[cite: 1]
            filter_mood = input("Nhập mức năng lượng để lọc (High/Neutral/Low) hoặc Enter để xem tất cả: ").strip().capitalize()
            
            display_tasks = tasks
            if filter_mood in ["High", "Neutral", "Low"]:
                display_tasks = [t for t in tasks if t.mood_affinity == filter_mood]
                print(f"\n[Đang lọc các công việc yêu cầu năng lượng: {filter_mood}]")
            elif filter_mood:
                print("Bộ lọc không hợp lệ, hiển thị tất cả.")
                
            if not display_tasks:
                print("Chưa có công việc nào khớp với điều kiện.")
            else:
                for i, t in enumerate(display_tasks):
                    status_icon = "✅" if t.status == "done" else "⏳"
                    print(f"{i+1}. [{status_icon}] {t.title} (⚡ {t.mood_affinity})")
                    
        elif choice == '4':
            pending_tasks = [(i, t) for i, t in enumerate(tasks) if t.status == 'pending']
            
            if not pending_tasks:
                print("\nKhông có công việc nào đang chờ xử lý.")
                continue
                
            print("\n--- HOÀN THÀNH CÔNG VIỆC ---")
            for idx, (original_idx, t) in enumerate(pending_tasks):
                print(f"{idx + 1}. {t.title} (⚡ {t.mood_affinity})")
            
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
                    
                    # Hành động hoàn thành task tự động đẩy trạng thái lên Active[cite: 1]
                    advance_state(session, "Active")
                else:
                    print("Lỗi: Số thứ tự không hợp lệ.")
            except ValueError:
                print("Lỗi: Vui lòng nhập một con số.")

        else:
            print("Lỗi: Menu không tồn tại. Vui lòng nhập số từ 0-4.")


if __name__ == "__main__":
    main()