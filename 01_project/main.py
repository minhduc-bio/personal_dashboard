import os
from datetime import date

from src import calendar_client
from src.models import Task
from src.storage import (
    init_storage,
    load_tasks,
    save_tasks,
    get_or_create_session,
    save_session,
)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(session):
    print("\n" + "=" * 45)
    print(f"BẢNG ĐIỀU KHIỂN - {session.date}")
    mood_str = f" | Mood: {session.mood}" if session.mood else ""
    print(f"Trạng thái phiên: [{session.state}]{mood_str}")
    print("=" * 45)


def show_calendar():
    print("\n--- LỊCH (Google Calendar - chỉ đọc) ---")
    try:
        events = calendar_client.list_upcoming_events()
    except FileNotFoundError as e:
        print(f"Lỗi: {e}")
        return
    except Exception as e:
        print(f"Không lấy được lịch: {e}")
        return

    if not events:
        print("Không có sự kiện sắp tới.")
        return
    for e in events:
        print(f"{e['start_display']} - {e['summary']}")


def set_mood(session):
    print("\n--- MOOD HÔM NAY ---")
    if session.mood:
        print(f"Mood hiện tại: {session.mood}")
        change = input("Đổi mood? (y/N): ").strip().lower()
        if change != 'y':
            return

    while True:
        mood = input("Bạn cảm thấy thế nào hôm nay (High/Neutral/Low, hoặc '0' để Hủy): ").strip()
        if mood == '0':
            return
        mood = mood.capitalize()
        if mood not in ("High", "Neutral", "Low"):
            print("Lỗi: chỉ nhận High, Neutral hoặc Low.")
            continue
        session.mood = mood
        # Đặt mood là hành động mở đầu ngày -> Planning
        session.advance_to("Planning")
        save_session(session)
        print(f"-> Đã ghi nhận mood: {mood}")
        return


def add_task(session, tasks):
    while True:
        title = input("\nNhập tên công việc (hoặc '0' để Hủy): ").strip()
        if title == '0':
            print("Đã hủy thêm công việc.")
            return
        if not title:
            print("Lỗi: Tên công việc không được để trống!")
            continue

        mood_affinity = input("Task này hợp với mood nào (High/Neutral/Low): ").strip().capitalize()
        if mood_affinity not in ("High", "Neutral", "Low"):
            print("Lỗi: chỉ nhận High, Neutral hoặc Low.")
            continue

        new_task = Task(title=title, mood_affinity=mood_affinity)
        tasks.append(new_task)
        save_tasks(tasks)

        session.task_ids.append(new_task.id)
        # Thêm task vào kế hoạch ngày -> Planning
        session.advance_to("Planning")
        save_session(session)

        print(f"-> Đã thêm thành công: '{title}' (mood: {mood_affinity})")
        return


def list_tasks(tasks, session):
    print("\n--- DANH SÁCH CÔNG VIỆC ---")
    if not tasks:
        print("Chưa có công việc nào.")
        return

    shown = tasks
    if session.mood:
        do_filter = input(f"Lọc theo mood hôm nay ({session.mood})? (y/N): ").strip().lower()
        if do_filter == 'y':
            shown = [t for t in tasks if t.mood_affinity == session.mood]
            if not shown:
                print(f"Không có công việc nào hợp mood {session.mood}.")
                return

    for i, t in enumerate(shown):
        status_icon = "✅" if t.status == "done" else "⏳"
        print(f"{i + 1}. [{status_icon}] {t.title} (mood: {t.mood_affinity})")


def complete_task(session, tasks):
    pending_tasks = [(i, t) for i, t in enumerate(tasks) if t.status == 'pending']

    if not pending_tasks:
        print("\nKhông có công việc nào đang chờ xử lý.")
        return

    print("\n--- HOÀN THÀNH CÔNG VIỆC ---")
    for idx, (_, t) in enumerate(pending_tasks):
        print(f"{idx + 1}. {t.title} (mood: {t.mood_affinity})")

    task_choice = input(
        f"\nChọn STT công việc đã xong (1-{len(pending_tasks)}, hoặc '0' để Hủy): "
    ).strip()
    if task_choice == '0':
        return

    try:
        selected_idx = int(task_choice) - 1
    except ValueError:
        print("Lỗi: Vui lòng nhập một con số.")
        return

    if not (0 <= selected_idx < len(pending_tasks)):
        print("Lỗi: Số thứ tự không hợp lệ.")
        return

    real_idx = pending_tasks[selected_idx][0]
    tasks[real_idx].status = 'done'
    save_tasks(tasks)

    # Hoàn thành task đầu tiên trong ngày -> Active (đang thực thi kế hoạch)
    session.advance_to("Active")
    save_session(session)

    print(f"-> Tuyệt vời! Đã hoàn thành: '{tasks[real_idx].title}' 🎉")


def end_of_day(session, tasks):
    print("\n--- KẾT THÚC NGÀY ---")
    confirm = input("Xác nhận đóng phiên hôm nay? Sẽ không thể mở lại. (y/N): ").strip().lower()
    if confirm != 'y':
        print("Đã hủy.")
        return

    session.advance_to("Reviewing")

    today_ids = set(session.task_ids)
    today_tasks = [t for t in tasks if t.id in today_ids]
    done_count = sum(1 for t in today_tasks if t.status == 'done')
    print(f"Tổng kết hôm nay: {done_count}/{len(today_tasks)} công việc hoàn thành.")

    session.advance_to("Closed")
    save_session(session)
    print("-> Phiên đã đóng. Hẹn gặp lại ngày mai!")


def pause():
    """Giữ kết quả hành động vừa rồi trên màn hình cho tới khi người dùng đọc xong,
    rồi mới clear để vẽ lại đúng 1 bảng điều khiển — tránh xả rác shell."""
    input("\n(Nhấn Enter để quay lại menu...)")


def main():
    init_storage()
    tasks = load_tasks()
    today_str = date.today().isoformat()
    session = get_or_create_session(today_str)

    while True:
        clear_screen()
        print_header(session)

        if session.state == "Closed":
            print("Phiên hôm nay đã đóng. Chỉ có thể thoát.")
            choice = input("\nNhập 0 để thoát: ").strip()
            if choice == '0':
                print("Tạm biệt!")
                break
            print("Lỗi: phiên đã đóng, không còn thao tác nào khác.")
            pause()
            continue

        print("1. Xem lịch Google Calendar")
        print("2. Đặt / xem Mood hôm nay")
        print("3. Thêm công việc mới (Task)")
        print("4. Xem danh sách công việc")
        print("5. Đánh dấu hoàn thành công việc")
        print("6. Kết thúc ngày")
        print("0. Thoát và Lưu")

        choice = input("\nChọn chức năng (0-6): ").strip()

        if choice == '0':
            print("Đã lưu dữ liệu. Tạm biệt!")
            break
        elif choice == '1':
            show_calendar()
            pause()
        elif choice == '2':
            set_mood(session)
            pause()
        elif choice == '3':
            add_task(session, tasks)
            pause()
        elif choice == '4':
            list_tasks(tasks, session)
            pause()
        elif choice == '5':
            complete_task(session, tasks)
            pause()
        elif choice == '6':
            end_of_day(session, tasks)
            pause()
        else:
            print("Lỗi: Menu không tồn tại. Vui lòng nhập số từ 0-6.")
            pause()


if __name__ == "__main__":
    main()