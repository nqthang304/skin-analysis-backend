import os
from dotenv import load_dotenv
from inference_sdk import InferenceHTTPClient

# Tải các biến môi trường từ file .env
load_dotenv()

# Khởi tạo client của Roboflow
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=ROBOFLOW_API_KEY
)

WORKSPACE_NAME = "phms-workspace-c4zjh"

def analyze_image_with_roboflow(image_path: str):
    """
    Hàm này nhận đường dẫn ảnh, chạy qua 3 mô hình Roboflow
    và trả về một Dictionary chứa các chỉ số đã trích xuất.
    """
    try:
        # 1. Gọi đồng thời 3 Workflow từ Roboflow
        res_physical = client.run_workflow(
            workspace_name=WORKSPACE_NAME,
            workflow_id="detect-count-and-visualize-3",
            images={"image": image_path}
        )
        res_skin_type = client.run_workflow(
            workspace_name=WORKSPACE_NAME,
            workflow_id="custom-workflow-4",
            images={"image": image_path}
        )
        res_pigment = client.run_workflow(
            workspace_name=WORKSPACE_NAME,
            workflow_id="custom-workflow-5",
            images={"image": image_path}
        )

        # 2. Trích xuất dữ liệu 
        output_image = res_physical[0].get('output_image', '') 
        
        # Mụn và Lỗ chân lông 
        acne_count = res_physical[0].get('ance_count_ob_output', 0)
        pore_count = res_physical[0].get('property_definition_output', 0)
        
        # Loại da 
        type_output = res_skin_type[0].get('model_output', {})
        skin_type_top = int(type_output.get('top', 4)) # Ép về số nguyên (int)
        
        # Sắc tố (Nằm trong 'model_output', key là 'top' chữ thường)
        pigment_output = res_pigment[0].get('model_output', {})
        pigment_top = int(pigment_output.get('top', 0)) 

        return {
            "status": "success",
            "data": {
                "output_image": output_image,
                "acne_count": acne_count,
                "pore_count": pore_count,
                "skin_type_index": skin_type_top,
                "pigment_index": pigment_top
            }
        }

    except Exception as e:
        print(f"Lỗi khi gọi Roboflow: {e}")
        return {
            "status": "error",
            "message": str(e)
        }