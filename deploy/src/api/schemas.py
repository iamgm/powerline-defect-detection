from pydantic import BaseModel
from typing import List, Optional, Tuple

class BoundingBox(BaseModel):
    # обычный прямоугольник для совместимости
    x1: float
    y1: float
    x2: float
    y2: float

class Detection(BaseModel):
    class_name: str
    class_id: int
    confidence: float
    
    # OBB - это список точек [[x,y], [x,y], [x,y], [x,y]]
    # делаем Optional, чтобы не ломать старый код
    polygon: Optional[List[Tuple[float, float]]] = None 
    
    # оставляем box для обратной совместимости
    box: BoundingBox

class PredictionResponse(BaseModel):
    filename: str
    image_size: List[int] # [width, height]
    model_used: str       # тип модели (small/large)
    detections: List[Detection]