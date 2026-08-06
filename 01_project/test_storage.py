from src.storage import init_storage, save_tasks, load_tasks
from src.models import Task

print("--- BẮT ĐẦU TEST STORAGE ---")

# 1. Khởi tạo thư mục
init_storage()
print("✅ Test 1: Khởi tạo thư mục data/ và data/sessions/ thành công.")

# 2. Tạo một danh sách Task giả định
my_tasks = [
    Task(
        id="t001", 
        title="Viết báo cáo tuần", 
        mood_affinity="High", 
        status="pending", 
        created_at="2026-08-06"
    ),
    Task(
        id="t002", 
        title="Dọn dẹp bàn làm việc", 
        mood_affinity="Neutral", 
        status="done", 
        created_at="2026-08-05"
    )
]

# 3. Test ghi file
save_tasks(my_tasks)
print("✅ Test 2: Đã lưu 2 tasks xuống file data/tasks.json.")

# 4. Test đọc file ngược lên
loaded_tasks = load_tasks()
print(f"✅ Test 3: Đã đọc lên {len(loaded_tasks)} tasks. Task đầu tiên là: {loaded_tasks[0].title}")