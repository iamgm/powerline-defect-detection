import io
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from PIL import Image
from typing import Literal

# импорты из наших модулей
from src.api.schemas import PredictionResponse
from src.ml.predictor import DefectPredictor

app = FastAPI(
    title="PowerLine Defect Detection API",
    description="API для детекции дефектов ЛЭП (YOLO OBB)",
    version="1.0.0"
)

# предиктор подгрузит модели только при первом запросе
predictor = DefectPredictor()

@app.get("/")
def health_check():
    return {
        "status": "ok", 
        "version": "1.0.0", 
        "models_available": list(predictor.weights_map.keys())
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_endpoint(
    file: UploadFile = File(...),
    # параметр выбора модели
    model_type: Literal["fast", "accurate"] = Query("fast", description="Выбор модели: fast (YOLO-S) или accurate (YOLO-L)"),
    # параметр порога уверенности (от 0.0 до 1.0)
    conf_threshold: float = Query(0.4, ge=0.0, le=1.0, description="Порог уверенности (Confidence Threshold)")
):
    """
    Принимает изображение и возвращает найденные объекты (OBB полигоны).
    """
    # валидация файла
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")

    try:
        # чтение картинки
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # передаем параметры в ML модуль 
        detections = predictor.predict(
            image=image, 
            model_key=model_type, 
            conf_threshold=conf_threshold
        )
        
        # формирование ответа
        return {
            "filename": file.filename,
            "image_size": [image.width, image.height],
            "model_used": model_type,
            "detections": detections
        }

    except Exception as e:
        print(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))