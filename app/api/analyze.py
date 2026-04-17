from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import os
from app.services.roboflow_api import analyze_image_with_roboflow
from app.services.gemini_api import get_ai_recommendation

router = APIRouter()

@router.post("/analyze-skin")
async def analyze_skin(
    file: UploadFile = File(...), 
    product_name: str = Form(...)
):
    try:
        # 1. Lưu file ảnh tạm thời để gửi đi phân tích
        file_location = f"temp_uploads/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        
        # 2. Gọi Roboflow để lấy các chỉ số "Vật lý"
        print("Đang gọi Roboflow...")
        roboflow_result = analyze_image_with_roboflow(file_location)
        
        if roboflow_result["status"] == "error":
            os.remove(file_location) # Dọn dẹp rác
            return JSONResponse(status_code=500, content={"message": "Lỗi hệ thống nhận diện ảnh"})

        metrics = roboflow_result["data"]
        
        # 3. Chuyển số liệu Roboflow sang cho Gemini "khám bệnh"
        print("Đang gọi Gemini...")
        ai_analysis = get_ai_recommendation(metrics, product_name)
        
        # 4. Xóa file ảnh tạm sau khi xong việc
        os.remove(file_location)
        
        # 5. Gói ghém kết quả trả về cho Frontend
        return {
            "status": "success",
            "roboflow_metrics": metrics,
            "expert_advice": ai_analysis
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})