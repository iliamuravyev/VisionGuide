!pip install ultralytics soundfile -q

import torch
import soundfile as sf
from PIL import Image
from google.colab import files
import IPython.display as ipd


# YOLOv5
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, force_reload=True, verbose=False)

# Silero TTS (локально)
device = torch.device('cpu')
torch.hub.download_url_to_file(
    'https://models.silero.ai/models/tts/ru/v4_ru.pt',
    'v4_ru.pt',
    progress=False
)
model_tts = torch.package.PackageImporter('v4_ru.pt').load_pickle("tts_models", "model")
model_tts.to(device)

SPEAKER = 'aidar'        # мужской голос
SAMPLE_RATE = 48000

def speak(text, speaker=SPEAKER, sample_rate=SAMPLE_RATE):
    return model_tts.apply_tts(text=text, speaker=speaker, sample_rate=sample_rate)

print("Загрузите фото (выберите файл):")
uploaded = files.upload()
img_path = list(uploaded.keys())[0]

results = model(img_path)
detections = results.pandas().xyxy[0]
img = Image.open(img_path)
img_height = img.size[1]

coco_to_russian = {
    'person': 'человек', 'bicycle': 'велосипед', 'car': 'машина',
    'motorcycle': 'мотоцикл', 'airplane': 'самолет', 'bus': 'автобус',
    'train': 'поезд', 'truck': 'грузовик', 'boat': 'лодка',
    'traffic light': 'светофор', 'fire hydrant': 'пожарный гидрант',
    'stop sign': 'знак стоп', 'parking meter': 'паркомат', 'bench': 'скамейка',
    'bird': 'птица', 'cat': 'кошка', 'dog': 'собака', 'horse': 'лошадь',
    'sheep': 'овца', 'cow': 'корова', 'elephant': 'слон', 'bear': 'медведь',
    'zebra': 'зебра', 'giraffe': 'жираф', 'backpack': 'рюкзак',
    'umbrella': 'зонт', 'handbag': 'сумка', 'tie': 'галстук',
    'suitcase': 'чемодан', 'frisbee': 'летающая тарелка', 'skis': 'лыжи',
    'snowboard': 'сноуборд', 'sports ball': 'мяч', 'kite': 'воздушный змей',
    'baseball bat': 'бейсбольная бита', 'baseball glove': 'бейсбольная перчатка',
    'skateboard': 'скейтборд', 'surfboard': 'доска для серфинга',
    'tennis racket': 'теннисная ракетка', 'bottle': 'бутылка',
    'wine glass': 'бокал', 'cup': 'чашка', 'fork': 'вилка',
    'knife': 'нож', 'spoon': 'ложка', 'bowl': 'миска', 'banana': 'банан',
    'apple': 'яблоко', 'sandwich': 'сэндвич', 'orange': 'апельсин',
    'broccoli': 'брокколи', 'carrot': 'морковь', 'hot dog': 'хот-дог',
    'pizza': 'пицца', 'donut': 'пончик', 'cake': 'торт',
    'chair': 'стул', 'couch': 'диван', 'potted plant': 'комнатное растение',
    'bed': 'кровать', 'dining table': 'обеденный стол', 'toilet': 'унитаз',
    'tv': 'телевизор', 'laptop': 'ноутбук', 'mouse': 'мышь',
    'remote': 'пульт', 'keyboard': 'клавиатура', 'cell phone': 'телефон',
    'microwave': 'микроволновка', 'oven': 'духовка', 'toaster': 'тостер',
    'sink': 'раковина', 'refrigerator': 'холодильник', 'book': 'книга',
    'clock': 'часы', 'vase': 'ваза', 'scissors': 'ножницы',
    'teddy bear': 'плюшевый мишка', 'hair drier': 'фен', 'toothbrush': 'зубная щетка'
}


exclude_classes = {'bird', 'airplane', 'kite'}

def get_distance_category(rel_height):
    if rel_height >= 0.4: return "очень близко"
    elif rel_height >= 0.2: return "близко"
    elif rel_height >= 0.1: return "на среднем расстоянии"
    elif rel_height >= 0.05: return "далеко"
    else: return "очень далеко"

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

# obstacles = []
# for _, row in detections.iterrows():
#     class_name = row['name']
#     russian_name = coco_to_russian.get(class_name, class_name)
#     bbox_height = row['ymax'] - row['ymin']
#     rel_height = bbox_height / img_height
#     obstacles.append(f"{russian_name} ({get_distance_category(rel_height)})")

if len(obstacles) == 0:
    description = "На фотографии нет объектов, мешающих проходу."
elif len(obstacles) == 1:
    description = f"На пути обнаружен: {obstacles[0]}."
else:
    objects_str = ", ".join(obstacles[:-1]) + " и " + obstacles[-1]
    description = f"На пути обнаружены: {objects_str}."

print("\n" + "="*50)
print(description)
print("="*50 + "\n")

audio_np = speak(description)
ipd.display(ipd.Audio(audio_np, rate=SAMPLE_RATE))

sf.write('output.wav', audio_np, SAMPLE_RATE)
results.save(save_dir='runs/detect/')