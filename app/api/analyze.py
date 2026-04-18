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
    file_location = None
    try:
        # 1. Lưu file ảnh tạm thời để gửi đi phân tích
        os.makedirs("temp_uploads", exist_ok=True)
        safe_filename = os.path.basename(file.filename)
        file_location = os.path.join("temp_uploads", safe_filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        
        # 2. Gọi Roboflow để lấy các chỉ số "Vật lý" (Raw metrics)
        print("Đang gọi Roboflow...")
        roboflow_result = analyze_image_with_roboflow(file_location)
        
        if roboflow_result.get("status") == "error":
            return JSONResponse(
                status_code=500, 
                content={"message": f"Lỗi hệ thống nhận diện ảnh: {roboflow_result.get('message', '')}"}
            )

        metrics = roboflow_result["data"]
        
        # 3. Gọi Gemini để "khám bệnh" và đánh giá sản phẩm
        print("Đang gọi Gemini...")
        ai_analysis = get_ai_recommendation(metrics, product_name)
        
        # Kiểm tra nếu Gemini ném ra lỗi trong quá trình call API
        if "error" in ai_analysis:
            return JSONResponse(status_code=500, content=ai_analysis)
        
        # 4. Gói ghém kết quả phân tầng rõ ràng cho Frontend
        return {
            "status": "success",
            "data": {
                "raw_metrics": metrics,                     # Dữ liệu gốc (để debug hoặc đếm số mụn)
                "scores": ai_analysis.get("scores", {}),    # Thang điểm 10 đã tính toán (Frontend dùng để vẽ biểu đồ)
                "consultation": {                           # Lời khuyên từ chuyên gia AI
                    "skin_analysis": ai_analysis.get("skin_analysis"),
                    "product_check": ai_analysis.get("product_check"),
                    "recommendations": ai_analysis.get("recommendations")
                }
            }
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        # 5. Dọn dẹp rác: Luôn xóa file ảnh tạm dù code chạy thành công hay lỗi
        if file_location and os.path.exists(file_location):
            os.remove(file_location)