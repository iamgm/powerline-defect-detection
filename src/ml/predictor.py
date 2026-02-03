import os
from PIL import Image
from ultralytics import YOLO
import torch

class DefectPredictor:
    def __init__(self):
        self.models = {} 
        self.active_model_name = None
        
        # пути к весам (локальные)
        self.weights_map = {
            "fast": "weights/yolo26s_obb_best.pt",
            "accurate": "weights/yolo26l_obb_best.pt"
        }
        
        # проверяем наличие GPU локально
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🚀 ML Service initialized on {self.device}")

    def load_model(self, model_key: str):
        """Ленивая загрузка модели"""
        if model_key not in self.weights_map:
            raise ValueError(f"Unknown model key: {model_key}")
            
        # если модель уже загружена - возвращаем её
        if model_key in self.models:
            return self.models[model_key]
        
        # если грузим новую, а памяти мало - опционально можно выгрузить старую
        # self.models.clear() 
        # torch.cuda.empty_cache()

        print(f"🔄 Loading model: {model_key}...")
        path = self.weights_map[model_key]
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model weights not found at {path}")
            
        model = YOLO(path)
        model.to(self.device)
        self.models[model_key] = model
        return model

    def predict(self, image: Image.Image, model_key: str = "fast", conf_threshold: float = 0.4):
        """
        Инференс
        """
        model = self.load_model(model_key)
        
        # инференс
        # imgsz можно меньше локально, но лучше 1024 как учили
        results = model.predict(image, conf=conf_threshold, imgsz=1024, verbose=False)
        result = results[0]
        
        formatted_detections = []
        
        # парсим OBB результаты
        if result.obb is not None:
            for i, cls_id in enumerate(result.obb.cls):
                cls_id = int(cls_id)
                conf = float(result.obb.conf[i])
                
                # xyxyxyxy - координаты 4 углов (полигон)
                # переводим тензор в список списков
                poly_tensor = result.obb.xyxyxyxy[i]
                # [[x1,y1], [x2,y2], ...]
                polygon = poly_tensor.cpu().numpy().tolist() 

                
                # xyxy - описывающий прямоугольник (для совместимости)
                box_tensor = result.obb.xyxy[i]
                x1, y1, x2, y2 = map(float, box_tensor.cpu().numpy())
                
                class_name = result.names[cls_id]
                
                formatted_detections.append({
                    "class_name": class_name,
                    "class_id": cls_id,
                    "confidence": conf,
                    "polygon": polygon,
                    "box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
                })
                
        return formatted_detections