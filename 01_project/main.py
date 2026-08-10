import datetime
import os

from src import calendar_client
from src.models import (
    Task,
    Goal,
    FlexibleSchedule,
    compute_score,
    compute_streak,
    compute_goal_progress,
    active_schedule,
    missed_schedules,
    check_stale_tasks,
)
from src.storage import (
    init_storage,
    load_tasks,
    save_tasks,
    load_goals,
    save_goals,
    load_schedules,
    save_schedules,
    get_or_create_session,
    save_session,
)
from src.timezone import APP_TZ, to_app_date


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def today_local():
    """Ngày hôm nay theo giờ ứng dụng (Asia/Ho_Chi_Minh)."""
    return datetime.datetime.now(APP_TZ).date()


def now_local():
    return datetime.datetime.now(APP_TZ)


def print_header(session, schedules):
    print("\n" + "=" * 45)
    print(f"BẢNG ĐIỀU KHIỂN - {session.date}")
    mood_str = f" | Mood: {session.mood}" if session.mood else ""
    print(f"Trạng thái phiên: [{session.state}]{mood_str}")

    missed = missed_schedules(schedules)
    if missed:
        print(f"⚠️  {len(missed)} lịch bị bỏ lỡ — xem mục 8 để xử lý")
    print("=" * 45)


MOOD_OPTIONS = ["High", "Neutral", "Low"]


def choose_mood(prompt: str, allow_cancel: bool = True):
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
    session.advance_to("Planning")
    save_session(session)
    print(f"-> Đã ghi nhận mood: {mood}")


def add_task(session, tasks, goals):
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

    goal_id = None
    if goals:
        print("\nGắn vào Goal nào? (để trống = không gắn Goal, Task-to-do thuần)")
        for i, g in enumerate(goals, start=1):
            print(f"{i}. {g.title}")
        goal_choice = input("Chọn số (Enter để bỏ qua): ").strip()
        if goal_choice:
            try:
                idx = int(goal_choice) - 1
                if 0 <= idx < len(goals):
                    goal_id = goals[idx].id
                else:
                    print("Số không hợp lệ, bỏ qua gắn Goal.")
            except ValueError:
                print("Không hợp lệ, bỏ qua gắn Goal.")

    new_task = Task(
        title=title, mood_affinity=mood_affinity, scheduled_date=scheduled_date, goal_id=goal_id
    )
    tasks.append(new_task)
    save_tasks(tasks)

    session.advance_to("Planning")
    save_session(session)

    schedule_label = "hôm nay" if scheduled_date else "chưa lên lịch"
    goal_label = f", Goal: {goal_id}" if goal_id else ""
    print(f"-> Đã thêm: '{title}' (mood: {mood_affinity}, {schedule_label}{goal_label})")


def _group_tasks(tasks):
    """Nhóm task theo status/scheduled_date. Paused tách riêng, không lẫn 3 nhóm kia."""
    today = today_local()
    overdue, today_tasks, unscheduled, paused = [], [], [], []
    for t in tasks:
        if t.status == 'paused':
            paused.append(t)
            continue
        if t.status != 'pending':
            continue
        if t.scheduled_date is None:
            unscheduled.append(t)
        elif t.scheduled_date < today:
            overdue.append(t)
        elif t.scheduled_date == today:
            today_tasks.append(t)
    return overdue, today_tasks, unscheduled, paused


def _task_stats_label(task, schedules):
    score = compute_score(task.id, schedules)
    streak = compute_streak(task.id, schedules)
    if score == 0 and streak == 0:
        return ""
    return f" [score: {score}, streak: {streak}]"


def list_tasks(tasks, schedules, session):
    print("\n--- CÔNG VIỆC ---")
    if not tasks:
        print("Chưa có công việc nào.")
        return

    overdue, today_tasks, unscheduled, paused = _group_tasks(tasks)

    apply_mood_filter = False
    if session.mood:
        do_filter = input(f"Lọc Today/Unscheduled theo mood hôm nay ({session.mood})? (y/N): ").strip().lower()
        apply_mood_filter = do_filter == 'y'

    if apply_mood_filter:
        today_tasks = [t for t in today_tasks if t.mood_affinity == session.mood]
        unscheduled = [t for t in unscheduled if t.mood_affinity == session.mood]

    def _print_group(label, group):
        print(f"\n{label} ({len(group)})")
        if not group:
            print("  (không có)")
            return
        for t in group:
            print(f"  - {t.title} (mood: {t.mood_affinity}){_task_stats_label(t, schedules)}")

    _print_group("🔴 Overdue", overdue)
    _print_group("🟡 Today's Tasks", today_tasks)
    _print_group("⚪ Unscheduled Tasks", unscheduled)
    _print_group("⏸️  Paused", paused)


def complete_task(session, tasks):
    """DONE TASK — hành động thủ công duy nhất để đóng Task, tách biệt hoàn
    toàn khỏi score/streak (dù score cao bao nhiêu cũng không tự động done)."""
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

    print("\n--- DONE TASK ---")
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

    session.advance_to("Active")
    save_session(session)

    print(f"-> Tuyệt vời! Đã hoàn thành: '{target.title}' 🎉")


def resume_task(tasks, schedules):
    """Resume: paused -> pending, kèm ngay bước tạo FlexibleSchedule mới —
    quay lại luôn đi kèm 1 cam kết cụ thể, không để đó mơ hồ."""
    paused_tasks = [t for t in tasks if t.status == 'paused']
    if not paused_tasks:
        print("\nKhông có công việc nào đang Paused.")
        return

    print("\n--- TIẾP TỤC CÔNG VIỆC (Resume) ---")
    for i, t in enumerate(paused_tasks):
        print(f"{i + 1}. {t.title}")

    choice = input(f"\nChọn STT (1-{len(paused_tasks)}, hoặc '0' để Hủy): ").strip()
    if choice == '0':
        return
    try:
        idx = int(choice) - 1
    except ValueError:
        print("Lỗi: Vui lòng nhập một con số.")
        return
    if not (0 <= idx < len(paused_tasks)):
        print("Lỗi: Số thứ tự không hợp lệ.")
        return

    target = paused_tasks[idx]
    target.resume()
    save_tasks(tasks)
    print(f"-> '{target.title}' đã quay lại Pending. Hãy đặt lịch buổi tiếp theo ngay:")
    _create_schedule_for_task(target, schedules)


def delete_task(tasks):
    if not tasks:
        print("\nChưa có công việc nào để xóa.")
        return

    today = today_local()

    def _label(t):
        if t.status == 'done':
            return "✅"
        if t.status == 'paused':
            return "⏸️"
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


# ==========================================
# GOAL (v1)
# ==========================================

def manage_goals(goals, tasks):
    while True:
        print("\n--- GOAL ---")
        print("1. Tạo Goal mới")
        print("2. Xem Goal & progress")
        print("0. Quay lại")
        choice = input("Chọn: ").strip()

        if choice == '0':
            return
        elif choice == '1':
            title = input("Tên Goal (hoặc '0' để Hủy): ").strip()
            if title == '0' or not title:
                continue
            new_goal = Goal(title=title)
            goals.append(new_goal)
            save_goals(goals)
            print(f"-> Đã tạo Goal: '{title}'")
        elif choice == '2':
            if not goals:
                print("Chưa có Goal nào.")
                continue
            for g in goals:
                done, total = compute_goal_progress(g.id, tasks)
                print(f"- {g.title}: {done}/{total} Task-goal-directed đã done")
        else:
            print("Lỗi: lựa chọn không hợp lệ.")


# ==========================================
# FLEXIBLE SCHEDULE (v1)
# ==========================================

def _prompt_datetime(label: str, default_days_ahead: int = 1, default_hm: str = "19:00"):
    """Hỏi ngày + giờ, trả về datetime aware theo APP_TZ. Enter = mặc định."""
    default_date = today_local() + datetime.timedelta(days=default_days_ahead)
    raw_date = input(f"{label} - Ngày (YYYY-MM-DD, Enter = {default_date.isoformat()}): ").strip()
    if raw_date:
        try:
            d = datetime.date.fromisoformat(raw_date)
        except ValueError:
            print("Lỗi định dạng ngày, dùng mặc định.")
            d = default_date
    else:
        d = default_date

    raw_time = input(f"{label} - Giờ (HH:MM, Enter = {default_hm}): ").strip() or default_hm
    try:
        h, m = map(int, raw_time.split(":"))
    except Exception:
        print("Lỗi định dạng giờ, dùng mặc định.")
        h, m = map(int, default_hm.split(":"))

    return datetime.datetime(d.year, d.month, d.day, h, m, tzinfo=APP_TZ)


def _create_schedule_for_task(task, schedules):
    existing = active_schedule(task.id, schedules)
    if existing:
        print(
            f"Task này đã có 1 buổi đang chờ ({existing.scheduled_start.strftime('%Y-%m-%d %H:%M')} "
            f"- {existing.scheduled_end.strftime('%H:%M')}). Hoàn thành hoặc xử lý buổi đó trước "
            f"(mục 8) trước khi tạo buổi mới."
        )
        return

    print(f"\nTạo buổi mới cho '{task.title}':")
    start = _prompt_datetime("Bắt đầu")
    duration_raw = input("Kéo dài bao lâu (giờ, Enter = 1): ").strip() or "1"
    try:
        duration_hours = float(duration_raw)
    except ValueError:
        print("Lỗi định dạng, dùng mặc định 1 giờ.")
        duration_hours = 1.0
    end = start + datetime.timedelta(hours=duration_hours)

    new_schedule = FlexibleSchedule(task_id=task.id, scheduled_start=start, scheduled_end=end)
    schedules.append(new_schedule)
    save_schedules(schedules)
    print(f"-> Đã đặt lịch: {start.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%H:%M')}")


def manage_schedules(tasks, schedules):
    while True:
        print("\n--- LỊCH BUỔI (FlexibleSchedule) ---")
        missed = missed_schedules(schedules)
        if missed:
            print(f"⚠️  {len(missed)} buổi đang bị bỏ lỡ")
        print("1. Tạo buổi mới cho 1 Task")
        print("2. Điểm danh buổi đang chờ")
        print("3. Xử lý buổi bị bỏ lỡ")
        print("0. Quay lại")
        choice = input("Chọn: ").strip()

        if choice == '0':
            return

        elif choice == '1':
            pending_tasks = [t for t in tasks if t.status == 'pending']
            if not pending_tasks:
                print("Không có Task pending nào.")
                continue
            for i, t in enumerate(pending_tasks):
                print(f"{i + 1}. {t.title}")
            sel = input("Chọn STT Task (hoặc '0' để Hủy): ").strip()
            if sel == '0':
                continue
            try:
                idx = int(sel) - 1
                if not (0 <= idx < len(pending_tasks)):
                    raise ValueError
            except ValueError:
                print("Lựa chọn không hợp lệ.")
                continue
            _create_schedule_for_task(pending_tasks[idx], schedules)

        elif choice == '2':
            waiting = [
                (t, active_schedule(t.id, schedules))
                for t in tasks
                if t.status == 'pending' and active_schedule(t.id, schedules) is not None
            ]
            if not waiting:
                print("Không có buổi nào đang chờ điểm danh.")
                continue
            for i, (t, s) in enumerate(waiting):
                print(f"{i + 1}. {t.title} — {s.scheduled_start.strftime('%Y-%m-%d %H:%M')} - {s.scheduled_end.strftime('%H:%M')}")
            sel = input("Chọn STT (hoặc '0' để Hủy): ").strip()
            if sel == '0':
                continue
            try:
                idx = int(sel) - 1
                if not (0 <= idx < len(waiting)):
                    raise ValueError
            except ValueError:
                print("Lựa chọn không hợp lệ.")
                continue
            _, sched = waiting[idx]
            sched.mark_completed()
            save_schedules(schedules)
            print("-> Đã điểm danh buổi này.")

        elif choice == '3':
            missed = missed_schedules(schedules)
            if not missed:
                print("Không có buổi nào bị bỏ lỡ.")
                continue
            task_by_id = {t.id: t for t in tasks}
            for s in missed:
                t = task_by_id.get(s.task_id)
                title = t.title if t else "(task không rõ)"
                print(f"\nBạn đã bỏ lỡ: '{title}' — {s.scheduled_start.strftime('%Y-%m-%d %H:%M')} - {s.scheduled_end.strftime('%H:%M')}")
                print("(1) Dời sang ngày mai cùng giờ  (2) Chọn ngày/giờ khác  (3) Bỏ qua")
                action = input("Chọn: ").strip()
                if action == '1':
                    s.mark_dismissed()
                    new_start = s.scheduled_start + datetime.timedelta(days=1)
                    new_end = s.scheduled_end + datetime.timedelta(days=1)
                    schedules.append(FlexibleSchedule(task_id=s.task_id, scheduled_start=new_start, scheduled_end=new_end))
                    print("-> Đã dời sang ngày mai cùng giờ.")
                elif action == '2':
                    s.mark_dismissed()
                    if t:
                        _create_schedule_for_task(t, schedules)
                elif action == '3':
                    s.mark_dismissed()
                    print("-> Đã bỏ qua, sẽ không nhắc lại buổi này.")
                else:
                    print("Bỏ qua lựa chọn không hợp lệ, giữ nguyên cảnh báo.")
            save_schedules(schedules)

        else:
            print("Lỗi: lựa chọn không hợp lệ.")


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
    input("\n(Nhấn Enter để quay lại menu...)")


def main():
    init_storage()
    tasks = load_tasks()
    goals = load_goals()
    schedules = load_schedules()
    today_str = today_local().isoformat()
    session = get_or_create_session(today_str)

    # Tự động pause Task không hoạt động quá PAUSE_THRESHOLD_DAYS — kiểm tra
    # 1 lần khi mở app, thông báo ngay nếu có Task vừa bị pause.
    newly_paused = check_stale_tasks(tasks, schedules, now_local())
    if newly_paused:
        save_tasks(tasks)

    while True:
        clear_screen()
        print_header(session, schedules)

        if newly_paused:
            names = ", ".join(f"'{t.title}'" for t in newly_paused)
            print(f"\n⏸️  Bạn đã từ bỏ quá lâu với: {names}.")
            print("Không sao — khi nào sẵn sàng quay lại, chúng ta tiếp tục nhé (mục 6 - Tiếp tục).")
            newly_paused = []  # chỉ thông báo 1 lần, không lặp lại mỗi vòng lặp
            pause()
            continue

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
        print("5. DONE TASK (đánh dấu hoàn thành)")
        print("6. Tiếp tục công việc đang Paused (Resume)")
        print("7. Xóa công việc")
        print("8. Goal")
        print("9. Lịch buổi (FlexibleSchedule)")
        print("10. Kết thúc ngày")
        print("11. Thoát và lưu")

        choice = input("\nChọn chức năng (1-11): ").strip()

        if choice == '11':
            print("Đã lưu dữ liệu. Tạm biệt!")
            break
        elif choice == '1':
            show_calendar()
            pause()
        elif choice == '2':
            set_mood(session)
            pause()
        elif choice == '3':
            add_task(session, tasks, goals)
            pause()
        elif choice == '4':
            list_tasks(tasks, schedules, session)
            pause()
        elif choice == '5':
            complete_task(session, tasks)
            pause()
        elif choice == '6':
            resume_task(tasks, schedules)
            pause()
        elif choice == '7':
            delete_task(tasks)
            pause()
        elif choice == '8':
            manage_goals(goals, tasks)
            pause()
        elif choice == '9':
            manage_schedules(tasks, schedules)
            pause()
        elif choice == '10':
            end_of_day(session, tasks)
            pause()
        else:
            print("Lỗi: Menu không tồn tại. Vui lòng nhập số từ 1-11.")
            pause()


if __name__ == "__main__":
    main()