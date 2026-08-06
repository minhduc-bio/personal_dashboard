from src.models import Task, Session

print("--- BẮT ĐẦU TEST SCHEMA ---")

# 1. Test tạo Task HỢP LỆ
try:
    valid_task = Task(
        id="t001",
        title="Viết báo cáo tuần",
        mood_affinity="High",
        status="pending",
        created_at="2026-08-06"
    )
    print("✅ Test 1: Tạo Task hợp lệ THÀNH CÔNG!")
    print(valid_task.model_dump_json(indent=2)) # In ra chuẩn JSON
except Exception as e:
    print("❌ Test 1 Thất bại:", e)

print("\n")

# 2. Test tạo Task KHÔNG HỢP LỆ (Sai status)
try:
    invalid_task = Task(
        id="t002",
        title="Công việc lỗi",
        mood_affinity="High",
        status="dang_lam", # Lỗi cố ý: status chỉ được là 'pending' hoặc 'done'
        created_at="2026-08-06"
    )
except Exception as e:
    print("✅ Test 2: Bắt lỗi sai Status THÀNH CÔNG! Chi tiết lỗi từ Pydantic:")
    print(e)