import os
import json
import google.genai as genai
from google.genai import types
from dotenv import load_dotenv

# Tải API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Khởi tạo Client theo chuẩn mới của Google
client = genai.Client(api_key=GEMINI_API_KEY)

def get_ai_recommendation(metrics_data: dict, product_name: str):
    prompt = f"""
    Bạn là một chuyên gia phân tích da liễu AI. 

    Nhiệm vụ 1: HÃY NHÌN VÀO BỨC ẢNH ĐÍNH KÈM VÀ ĐÁNH GIÁ CHẤT LƯỢNG ẢNH. 
    Bức ảnh này có dấu hiệu trang điểm đậm, dùng phần mềm làm mịn da (filter), hay ánh sáng quá ảo không? Nếu có, hãy cảnh báo người dùng.

    Nhiệm vụ 2: Dựa trên các chỉ số đo lường thực tế dưới đây, hãy phân tích tình trạng da và đánh giá sản phẩm.
    - Tổng số mụn: {metrics_data.get('acne_count')}
    - Tổng số lỗ chân lông to: {metrics_data.get('pore_count')}
    - Phân loại da (1-9): {metrics_data.get('skin_type_index')}
    - Chỉ số sắc tố (0-9): {metrics_data.get('pigment_index')}
    - Sản phẩm: {product_name}

   Hãy trả về BẮT BUỘC theo cấu trúc JSON sau:
    {{
      "image_quality_warning": "Chuỗi rỗng nếu ảnh hợp lệ. Hoặc ghi lời cảnh báo nếu phát hiện ảnh có trang điểm/dùng app làm mịn da.",
      "skin_analysis": {{
        "status": "Mô tả ngắn gọn về da",
        "primary_concerns": ["Vấn đề 1", "Vấn đề 2"]
      }},
      "product_check": {{
        "name": "{product_name}",
        "is_compatible": true,
        "compatibility_score": 85,
        "detailed_analysis": "Tại sao hợp/không hợp?",
        "ingredients_of_concern": ["Thành phần rủi ro"],
        "beneficial_ingredients": ["Thành phần tốt"]
      }},
      "recommendations": [
        {{
          "name": "Sản phẩm 1",
          "brand": "Thương hiệu",
          "reason": "Lý do"
        }}
      ]
    }}
    """
    
    try:
        # Cú pháp gọi API theo thư viện mới
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        # Dọn dẹp JSON
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        result_json = json.loads(cleaned_text)
        return result_json
        
    except Exception as e:
        print(f"======== LỖI GEMINI CỤ THỂ ========")
        print(e)
        return {"error": "Lỗi xử lý Gemini", "detail": str(e)}