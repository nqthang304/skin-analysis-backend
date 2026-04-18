import os
import json
import google.genai as genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def calculate_skin_scores(metrics_data: dict):
    """Tính toán thang điểm 10 và tìm ra vấn đề nghiêm trọng nhất"""
    acne = metrics_data.get('acne_count', 0)
    pores = metrics_data.get('pore_count', 0)
    skin_type = metrics_data.get('skin_type_index', 4)
    pigment = metrics_data.get('pigment_index', 0)

    # 1. Tính điểm 
    acne_score = max(0.0, 10.0 - (acne * 0.5))          # Mỗi nốt mụn trừ 0.5 điểm
    pore_score = max(0.0, 10.0 - (pores * 0.05))        # Mỗi lỗ chân lông trừ 0.05 điểm
    pigment_score = max(0.0, 10.0 - pigment)            # Điểm 10 trừ đi chỉ số sắc tố
    balance_score = max(0.0, 10.0 - (abs(skin_type - 3.5) * 1.8)) # Dựa trên khoảng cách tới mốc lý tưởng 3.5
    
    # Tính điểm tổng quát với trọng số mới (Mụn 30%, Lỗ chân lông 15%, Sắc tố 35%, Cân bằng 20%)
    overall_score = (acne_score * 0.30) + (pore_score * 0.15) + (pigment_score * 0.35) + (balance_score * 0.20)

    # 2. Phân loại loại da bằng text
    if skin_type <= 2:
        skin_text = "Da khô đến rất khô"
    elif skin_type <= 5:
        skin_text = "Da thường đến hỗn hợp"
    else:
        skin_text = "Da dầu đến rất dầu"

    # 3. Tìm vấn đề ưu tiên (Điểm nào thấp nhất trong 4 chỉ số)
    scores = {
        "Mụn": acne_score,
        "Lỗ chân lông to": pore_score,
        "Sắc tố (thâm, nám, không đều màu)": pigment_score,
        "Độ cân bằng ẩm/dầu": balance_score
    }
    primary_issue = min(scores, key=scores.get)

    return {
        "acne_score": round(acne_score, 1),
        "pore_score": round(pore_score, 1),
        "pigment_score": round(pigment_score, 1),
        "balance_score": round(balance_score, 1),
        "overall_score": round(overall_score, 1),
        "skin_text": skin_text,
        "primary_issue": primary_issue,
        "raw_acne": acne,
        "raw_pores": pores
    }

def get_ai_recommendation(metrics_data: dict, product_name: str):
    analysis = calculate_skin_scores(metrics_data)
    
    prompt = f"""
    Bạn là một Bác sĩ da liễu AI. 

    Nhiệm vụ 1: Phân tích tình trạng da dựa trên dữ liệu hệ thống đã chấm điểm (Thang điểm 10):
    - Tình trạng tổng quát: Đạt {analysis['overall_score']}/10 điểm.
    - Phân loại da: {analysis['skin_text']} (Điểm cân bằng đạt {analysis['balance_score']}/10).
    - Tình trạng mụn: Đạt {analysis['acne_score']}/10 (Phát hiện {analysis['raw_acne']} nốt mụn).
    - Tình trạng lỗ chân lông: Đạt {analysis['pore_score']}/10 (Phát hiện {analysis['raw_pores']} lỗ chân lông to).
    - Độ đều màu (Sắc tố): Đạt {analysis['pigment_score']}/10.

    => CHẨN ĐOÁN HỆ THỐNG: Vấn đề nghiêm trọng nhất cần ưu tiên giải quyết hiện tại là: "{analysis['primary_issue']}".

    Nhiệm vụ 2: Đánh giá sản phẩm người dùng đang hỏi: "{product_name}". 
    Dựa vào tình trạng da và vấn đề ưu tiên ở trên, sản phẩm này có phù hợp không? TỰ ĐÁNH GIÁ điểm tương thích từ 0-100.
    Gợi ý thêm 1-2 sản phẩm khác tốt hơn hoặc bổ trợ tốt cho việc điều trị "{analysis['primary_issue']}".

    Hãy trả về BẮT BUỘC theo cấu trúc JSON chuẩn dưới đây (Lưu ý: is_compatible phải là boolean thực sự, compatibility_score phải là số nguyên):
    {{
      "skin_analysis": {{
        "status": "Mô tả chuyên sâu về tình trạng da hiện tại dựa trên các điểm số.",
        "primary_concerns": ["Vấn đề ưu tiên 1", "Vấn đề 2"],
        "expert_routine_advice": "Lời khuyên skincare routine nên tập trung vào điều gì để giải quyết vấn đề ưu tiên nhất?"
      }},
      "product_check": {{
        "name": "{product_name}",
        "is_compatible": true,
        "compatibility_score": 85,
        "detailed_analysis": "Tại sao hợp/không hợp với tình trạng da trên?",
        "ingredients_of_concern": ["Thành phần rủi ro nếu có"],
        "beneficial_ingredients": ["Thành phần tốt nếu có"]
      }},
      "recommendations": [
        {{
          "name": "Tên sản phẩm",
          "brand": "Thương hiệu",
          "reason": "Lý do khuyên dùng"
        }}
      ]
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        result_json = json.loads(cleaned_text)
        
        # ĐÍNH KÈM ĐIỂM SỐ VÀO RESPONSE ĐỂ FRONTEND RENDER BIỂU ĐỒ
        result_json["scores"] = analysis 
        
        return result_json
        
    except Exception as e:
        print(f"======== LỖI GEMINI ========\n{e}")
        return {"error": "Lỗi xử lý Gemini", "detail": str(e)}