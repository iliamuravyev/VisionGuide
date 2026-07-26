import cv2
import torch
import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Подключаем статику (папка static)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Загрузка модели YOLO
print("Загрузка YOLOv5...")
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, verbose=False)

# Словарь перевода
coco_to_russian = {
    'person': 'человек', 'bicycle': 'велосипед', 'car': 'машина',
    'motorcycle': 'мотоцикл', 'airplane': 'самолет', 'bus': 'автобус',
    'train': 'поезд', 'truck': 'грузовик', 'boat': 'лодка',
    'traffic light': 'светофор', 'bench': 'скамейка',
    'bird': 'птица', 'cat': 'кошка', 'dog': 'собака', 'horse': 'лошадь',
    'sheep': 'овца', 'cow': 'корова', 'elephant': 'слон', 'bear': 'медведь',
    'zebra': 'зебра', 'giraffe': 'жираф', 'backpack': 'рюкзак',
    'umbrella': 'зонт', 'handbag': 'сумка', 'tie': 'галстук',
    'suitcase': 'чемодан', 'skis': 'лыжи', 'snowboard': 'сноуборд',
    'skateboard': 'скейтборд', 'surfboard': 'доска для серфинга',
    'bottle': 'бутылка', 'cup': 'чашка', 'fork': 'вилка',
    'knife': 'нож', 'spoon': 'ложка', 'bowl': 'миска', 'banana': 'банан',
    'apple': 'яблоко', 'sandwich': 'сэндвич', 'orange': 'апельсин',
    'pizza': 'пицца', 'donut': 'пончик', 'cake': 'торт',
    'chair': 'стул', 'couch': 'диван', 'potted plant': 'комнатное растение',
    'bed': 'кровать', 'dining table': 'обеденный стол', 'toilet': 'унитаз',
    'tv': 'телевизор', 'laptop': 'ноутбук', 'mouse': 'мышь',
    'keyboard': 'клавиатура', 'cell phone': 'телефон', 'book': 'книга',
    'clock': 'часы', 'vase': 'ваза'
}

def get_distance_category(rel_height):
    if rel_height >= 0.4: return "очень близко"
    elif rel_height >= 0.2: return "близко"
    elif rel_height >= 0.1: return "на среднем расстоянии"
    elif rel_height >= 0.05: return "далеко"
    else: return "очень далеко"

def process_image(image_bytes: bytes) -> str:
    """Принимает байты изображения, возвращает текстовое описание."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return "Не удалось декодировать изображение"
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    img_height = img.shape[0]
    results = model(img_pil)
    detections = results.pandas().xyxy[0]

    exclude_classes = {'bird', 'airplane', 'kite'}
    obstacles = []
    for _, row in detections.iterrows():
        class_name = row['name']
        if class_name in exclude_classes:
            continue
        bbox_height = row['ymax'] - row['ymin']
        rel_height = bbox_height / img_height
        ymax_norm = row['ymax'] / img_height
        if ymax_norm > 0.4 and rel_height > 0.04:
            russian_name = coco_to_russian.get(class_name, class_name)
            obstacles.append(f"{russian_name} ({get_distance_category(rel_height)})")

    if len(obstacles) == 0:
        return "На снимке нет объектов, мешающих проходу."
    elif len(obstacles) == 1:
        return f"На пути обнаружен: {obstacles[0]}."
    else:
        objects_str = ", ".join(obstacles[:-1]) + " и " + obstacles[-1]
        return f"На пути обнаружены: {objects_str}."

# Главная страница – отдаём HTML
@app.get("/", response_class=HTMLResponse)
async def index():
    # Читаем содержимое templates/index.html
    with open("static/templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Эндпоинт для загрузки изображения
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if file.filename == "":
        raise HTTPException(status_code=400, detail="Файл не выбран")
    # Проверяем расширение (необязательно)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл не является изображением")
    try:
        image_bytes = await file.read()
        description = process_image(image_bytes)
        print(3643)
        return JSONResponse(content={"description": description})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Точка входа для запуска через uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)