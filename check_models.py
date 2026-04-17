import os
from google import genai
from dotenv import load_dotenv

# Tải API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Kết nối
client = genai.Client(api_key=GEMINI_API_KEY)

print("Đang quét danh sách các mô hình AI khả dụng cho API Key của bạn...")
print("-" * 50)

# Lấy danh sách và in ra màn hình
for m in client.models.list():
    # Chỉ in ra các model hỗ trợ tạo văn bản (generateContent)
    if "generateContent" in m.supported_actions:
        print(f"Tên chuẩn: {m.name}")