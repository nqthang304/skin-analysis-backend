import os

# Danh sách các thư mục cần tạo
folders = [
    "app/api",
    "app/core",
    "app/schemas",
    "app/services",
    "temp_uploads"
]

# Danh sách các file cần tạo
files = [
    "app/__init__.py",
    "app/main.py",
    "app/api/__init__.py",
    "app/api/analyze.py",
    "app/core/__init__.py",
    "app/core/config.py",
    "app/schemas/__init__.py",
    "app/schemas/response_models.py",
    "app/services/__init__.py",
    "app/services/roboflow_api.py",
    "app/services/gemini_api.py",
    ".env",
    ".gitignore",
    "requirements.txt"
]

# 1. Tạo thư mục
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"📁 Đã tạo thư mục: {folder}")

# 2. Tạo file trống
for file in files:
    with open(file, "w", encoding="utf-8") as f:
        # Ghi sẵn một số nội dung cơ bản cho các file quan trọng
        if file == "requirements.txt":
            f.write("fastapi\nuvicorn\npython-multipart\ninference-sdk\ngoogle-generativeai\npython-dotenv\n")
        elif file == ".gitignore":
            f.write(".env\n__pycache__/\ntemp_uploads/\n")
        elif file == ".env":
            f.write("ROBOFLOW_API_KEY=\nGEMINI_API_KEY=\n")
        pass
    print(f"📄 Đã tạo file: {file}")

print("\n✅ THÀNH CÔNG! Đã khởi tạo xong cấu trúc dự án.")