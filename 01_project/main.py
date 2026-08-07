import datetime
import os

from src import calendar_client
from src.models import Task
from src.storage import (
    init_storage,
    load_tasks,
    save_tasks,
    get_or_create_session,
    save_session,
)
from src.timezone import APP_TZ, to_app_date


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def today_local():
    """Ngày hôm nay theo giờ ứng dụng (Asia/Ho_Chi_Minh) — dùng nhất quán ở
    mọi nơi cần biết 'hôm nay' (session.date, scheduled_date, so sánh Overdue),
    thay vì phụ thuộc timezone của hệ điều hành máy chạy app."""
    return datetime.datetime.now(APP_TZ).date()


def print_header(session):
    print("\n" + "=" * 45)
    print(f"BẢNG ĐIỀU KHIỂN - {session.date}")
    mood_str = f" | Mood: {session.mood}" if session.mood else ""
    print(f"Trạng thái phiên: [{session.state}]{mood_str}")
    print("=" * 45)


MOOD_OPTIONS = ["High", "Neutral", "Low"]


def choose_mood(prompt: str, allow_cancel: bool = True):
    """Cho chọn mood bằng số (1/2/3) thay vì gõ text tự do — loại bỏ hẳn lỗi
    chính tả/viết hoa-thường. Trả về None nếu người dùng hủy (allow_cancel=True)."""
    print(f"\n{prompt}")
    for i, m in enumerate(MOOD_OPTIONS, start=1):
        print(f"{i}. {m}")
    if allow_cancel:
        print("0. Hủy")

    while True:
        choice = input("Chọn (số): ").strip()
        if allow_cancel and choice == '0':
            return None
        if choice in ('1', '2', '3'):
            return MOOD_OPTIONS[int(choice) - 1]
        valid = "1, 2, 3" + (" hoặc 0 để hủy" if allow_cancel else "")
        print(f"Lỗi: chỉ nhận {valid}.")


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

    mood = choose_mood("Bạn cảm thấy thế nào hôm nay?")
    if mood is None:
        return

    session.mood = mood
    # Đặt mood là hành động mở đầu ngày -> Planning
    session.advance_to("Planning")
    save_session(session)
    print(f"-> Đã ghi nhận mood: {mood}")


def add_task(session, tasks):
    while True:
        title = input("\nNhập tên công việc (hoặc '0' để Hủy): ").strip()
        if title == '0':
            print("Đã hủy thêm công việc.")
            return
        if not title:
            print("Lỗi: Tên công việc không được để trống!")
            continue
        break

    mood_affinity = choose_mood("Task này hợp với mood nào?")
    if mood_affinity is None:
        print("Đã hủy thêm công việc.")
        return

    schedule_today = input("Lên lịch cho hôm nay? (y/N — để trống = chưa lên lịch): ").strip().lower()
    scheduled_date = today_local() if schedule_today == 'y' else None

    new_task = Task(title=title, mood_affinity=mood_affinity, scheduled_date=scheduled_date)
    tasks.append(new_task)
    save_tasks(tasks)

    # Thêm task vào kế hoạch -> Planning
    session.advance_to("Planning")
    save_session(session)

    schedule_label = "hôm nay" if scheduled_date else "chưa lên lịch"
    print(f"-> Đã thêm: '{title}' (mood: {mood_affinity}, {schedule_label})")


def _group_tasks(tasks):
    """Phân nhóm task PENDING theo scheduled_date so với hôm nay:
    🔴 Overdue (scheduled < hôm nay), 🟡 Today (scheduled == hôm nay),
    ⚪ Unscheduled (chưa có scheduled_date). Task đã done không nằm trong
    3 nhóm này — xem đầy đủ lịch sử qua danh sách Xóa công việc (mục 6)."""
    today = today_local()
    overdue, today_tasks, unscheduled = [], [], []
    for t in tasks:
        if t.status != 'pending':
            continue
        if t.scheduled_date is None:
            unscheduled.append(t)
        elif t.scheduled_date < today:
            overdue.append(t)
        elif t.scheduled_date == today:
            today_tasks.append(t)
        # scheduled_date > today (lên lịch tương lai) -> chưa có trong MVP này,
        # tạm không hiển thị ở đâu cả (chưa cần Reschedule / future view ở MVP)
    return overdue, today_tasks, unscheduled


def list_tasks(tasks, session):
    print("\n--- CÔNG VIỆC ---")
    if not tasks:
        print("Chưa có công việc nào.")
        return

    overdue, today_tasks, unscheduled = _group_tasks(tasks)

    apply_mood_filter = False
    if session.mood:
        do_filter = input(f"Lọc Today/Unscheduled theo mood hôm nay ({session.mood})? (y/N): ").strip().lower()
        apply_mood_filter = do_filter == 'y'

    if apply_mood_filter:
        # Overdue KHÔNG lọc theo mood — task quá hạn phải luôn hiện đủ để không bị
        # "biến mất khỏi tầm mắt" chỉ vì không hợp mood hôm nay.
        today_tasks = [t for t in today_tasks if t.mood_affinity == session.mood]
        unscheduled = [t for t in unscheduled if t.mood_affinity == session.mood]

    def _print_group(label, group):
        print(f"\n{label} ({len(group)})")
        if not group:
            print("  (không có)")
            return
        for t in group:
            print(f"  - {t.title} (mood: {t.mood_affinity})")

    _print_group("🔴 Overdue", overdue)
    _print_group("🟡 Today's Tasks", today_tasks)
    _print_group("⚪ Unscheduled Tasks", unscheduled)


def complete_task(session, tasks):
    pending_tasks = [t for t in tasks if t.status == 'pending']
    if not pending_tasks:
        print("\nKhông có công việc nào đang chờ xử lý.")
        return

    today = today_local()

    def _label(t):
        if t.scheduled_date is None:
            return "⚪"
        if t.scheduled_date < today:
            return "🔴"
        if t.scheduled_date == today:
            return "🟡"
        return "⚪"

    print("\n--- HOÀN THÀNH CÔNG VIỆC ---")
    for idx, t in enumerate(pending_tasks):
        print(f"{idx + 1}. {_label(t)} {t.title} (mood: {t.mood_affinity})")

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

    target = pending_tasks[selected_idx]
    target.mark_done()
    save_tasks(tasks)

    # Hoàn thành task đầu tiên trong ngày -> Active (đang thực thi kế hoạch)
    session.advance_to("Active")
    save_session(session)

    print(f"-> Tuyệt vời! Đã hoàn thành: '{target.title}' 🎉")


def delete_task(tasks):
    if not tasks:
        print("\nChưa có công việc nào để xóa.")
        return

    today = today_local()

    def _label(t):
        if t.status == 'done':
            return "✅"
        if t.scheduled_date is None:
            return "⚪"
        if t.scheduled_date < today:
            return "🔴"
        return "🟡"

    print("\n--- XÓA CÔNG VIỆC ---")
    for i, t in enumerate(tasks):
        print(f"{i + 1}. {_label(t)} {t.title} (mood: {t.mood_affinity})")

    task_choice = input(
        f"\nChọn STT công việc muốn xóa (1-{len(tasks)}, hoặc '0' để Hủy): "
    ).strip()
    if task_choice == '0':
        return

    try:
        selected_idx = int(task_choice) - 1
    except ValueError:
        print("Lỗi: Vui lòng nhập một con số.")
        return

    if not (0 <= selected_idx < len(tasks)):
        print("Lỗi: Số thứ tự không hợp lệ.")
        return

    target = tasks[selected_idx]
    confirm = input(f"Xác nhận xóa '{target.title}'? Không thể hoàn tác (y/N): ").strip().lower()
    if confirm != 'y':
        print("Đã hủy.")
        return

    tasks.pop(selected_idx)
    save_tasks(tasks)
    print(f"-> Đã xóa: '{target.title}'")


def end_of_day(session, tasks):
    print("\n--- KẾT THÚC NGÀY ---")
    confirm = input("Xác nhận đóng phiên hôm nay? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Đã hủy.")
        return

    session.advance_to("Reviewing")

    today = today_local()
    completed_today = [
        t for t in tasks if t.completed_at is not None and to_app_date(t.completed_at) == today
    ]
    scheduled_today_pending = [
        t for t in tasks if t.status == 'pending' and t.scheduled_date == today
    ]

    print(f"Hoàn thành hôm nay: {len(completed_today)} công việc.")
    print(f"Còn {len(scheduled_today_pending)} công việc lên lịch hôm nay chưa xong.")

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
    today_str = today_local().isoformat()
    session = get_or_create_session(today_str)

    while True:
        clear_screen()
        print_header(session)

        if session.state == "Closed":
            print("Phiên hôm nay đã đóng.")
            print("0. Thoát")
            print("r. Mở lại phiên (CHỈ DÙNG KHI TEST — không dùng lúc vận hành thật)")
            choice = input("\nChọn (0/r): ").strip().lower()
            if choice == '0':
                print("Tạm biệt!")
                break
            if choice == 'r':
                confirm = input(
                    "Xác nhận mở lại phiên để test? Việc này KHÔNG phản ánh vòng đời "
                    "thật của một ngày làm việc (y/N): "
                ).strip().lower()
                if confirm == 'y':
                    session.force_reopen("Active")
                    save_session(session)
                    print("-> Đã mở lại phiên (state: Active).")
                pause()
                continue
            print("Lỗi: phiên đã đóng, chỉ nhận 0 hoặc r.")
            pause()
            continue

        print("1. Xem lịch Google Calendar")
        print("2. Xem / đặt Mood hôm nay")
        print("3. Thêm công việc mới")
        print("4. Xem công việc")
        print("5. Đánh dấu hoàn thành")
        print("6. Xóa công việc")
        print("7. Kết thúc ngày")
        print("8. Thoát và lưu")

        choice = input("\nChọn chức năng (1-8): ").strip()

        if choice == '8':
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
            delete_task(tasks)
            pause()
        elif choice == '7':
            end_of_day(session, tasks)
            pause()
        else:
            print("Lỗi: Menu không tồn tại. Vui lòng nhập số từ 1-8.")
            pause()


if __name__ == "__main__":
    main()