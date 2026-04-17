from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import analyze

# Khởi tạo ứng dụng FastAPI và gán vào biến "app"
app = FastAPI(title="Skin Analysis API")

# Cấu hình CORS (Bắt buộc để React ở Frontend có thể gọi được API này)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kết nối file api/analyze.py vào hệ thống
app.include_router(analyze.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Backend AI Đánh Giá Da đang hoạt động bình thường!"}