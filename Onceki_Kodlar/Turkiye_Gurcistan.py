import cv2
from ultralytics import YOLO
import numpy as np
from sklearn.cluster import KMeans

# Modeli yükle
model = YOLO("../model/bestdeneme.pt")

# Video dosyasını aç
video_path = "../Videos/Turkiye.mp4"
cap = cv2.VideoCapture(video_path)

# Class isimleri (index sırasına göre)
class_names = [
    'Player',
    'GoalKeeper',
    'Ball',
    'Main Referee',
    'Side Referee',
    'Staff Member'
]

# Eşik değerleri (confidence threshold)
class_thresholds = {
    'Side Referee': 0.5,
    'Main Referee': 0.5,
    'Player': 0.63,
    'Staff Member': 0.7,
    'Ball': 0.5,
    'GoalKeeper': 0.5
}

# Renkler (BGR formatında)
class_colors = {
    'Gurcistan': (0, 255, 0),         # Yeşil (takım A)
    'Turkiye': (0, 140, 255),     # Turuncu-Sarı (takım B)
    'Ball': (0, 0, 255),              # Kırmızı
    'Side Referee': (255, 0, 0),      # Mavi
    'Main Referee': (255, 100, 0),    # Turuncu
    'Staff Member': (128, 0, 128),     # Mor
    'GoalKeeper': (0, 255, 255)       # Sarı-Mavi (açık camgöbeği gibi)
}

# Takım renk kümeleri (HSV formatında)
team_a_color = None
team_b_color = None
Turkiye = cv2.imread("../Forma/Turkiye.png")
Hsv_Turkiye = cv2.cvtColor(Turkiye, cv2.COLOR_BGR2HSV)
ortalama_turkiye = np.array(cv2.mean(Hsv_Turkiye)[:3])

Gurcistan = cv2.imread("../Forma/Gurcistan.png")
Hsv_Gurcistan = cv2.cvtColor(Gurcistan, cv2.COLOR_BGR2HSV)
ortalama_gurcistan = np.array(cv2.mean(Hsv_Gurcistan)[:3])

print("Gurcistan", ortalama_gurcistan[1])
print("Turkiye" , ortalama_turkiye[1])

if ortalama_turkiye[1] < ortalama_gurcistan[1]:
    team_a_color = ortalama_turkiye
else:
    team_b_color = ortalama_gurcistan

def get_hsv_mean(image, box):
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cropped = image[y1:y2, x1:x2]
    if cropped.size == 0:
        return np.array([0, 0, 0])
    hsv_image = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
    return np.array(cv2.mean(hsv_image)[:3])

def initialize_team_colors(detections, frame):
    hsv_values = []
    for box in detections:
        if class_names[int(box.cls[0].item())] == 'Player':
            hsv_mean = get_hsv_mean(frame, box)
            if hsv_mean is not None:
                hsv_values.append(hsv_mean)

    if len(hsv_values) < 2:
        return False

    # K-Means ile 2 küme oluştur
    kmeans = KMeans(n_clusters=2, random_state=0).fit(hsv_values)
    global team_a_color, team_b_color
    colors = kmeans.cluster_centers_
    # S (saturation) değeri küçük olan Gürcistan olsun
    if colors[0][1] < colors[1][1]:
        team_a_color, team_b_color = colors[0], colors[1]
    else:
        team_a_color, team_b_color = colors[1], colors[0]
    return True

def classify_player(hsv_value):
    dist_to_a = np.linalg.norm(hsv_value - team_a_color)
    dist_to_b = np.linalg.norm(hsv_value - team_b_color)
    print(team_a_color, team_b_color)
    return "Gurcistan" if dist_to_a < dist_to_b else "Turkiye"

initialized = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    result = results[0]
    boxes = result.boxes

    annotated_frame = frame.copy()

    # Player kutucuklarını al
    player_boxes = [box for box in boxes if class_names[int(box.cls[0].item())] == 'Player']

    # Takım renkleri için ilk başlatma
    if not initialized and len(player_boxes) >= 9:
        if initialize_team_colors(player_boxes, frame):
            initialized = True
            print("Takım renkleri başarıyla belirlendi!")

    # En yüksek güvenilirlikte referee ve topu bulmak için
    top_side_referee = None
    top_main_referee = None
    top_ball = None

    if boxes is not None:
        for box in boxes:
            cls_id = int(box.cls[0].item())
            conf = box.conf[0].item()
            class_name = class_names[cls_id]

            # Eşik kontrolü
            if conf < class_thresholds.get(class_name, 0.5):
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            if class_name == 'Main Referee':
                if top_main_referee is None or conf > top_main_referee['conf']:
                    top_main_referee = {'box': box, 'conf': conf}
            elif class_name == 'Player':
                hsv_mean = get_hsv_mean(frame, box)

                team = classify_player(hsv_mean) if initialized else "Unknown"

                label = f"{team} {conf:.2f}"
                color = class_colors.get(team, (255, 255, 255))
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(annotated_frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            elif class_name == 'Side Referee':
                if top_side_referee is None or conf > top_side_referee['conf']:
                    top_side_referee = {'box': box, 'conf': conf}



            elif class_name == 'Ball':
                if top_ball is None or conf > top_ball['conf']:
                    top_ball = {'box': box, 'conf': conf}

            else:  # Staff Member, GoalKeeper gibi diğer sınıflar
                label = f"{class_name} {conf:.2f}"
                color = class_colors.get(class_name, (255, 255, 255))
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(annotated_frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # En güvenilir Side Referee kutusunu çiz
    if top_side_referee:
        box = top_side_referee['box']
        conf = top_side_referee['conf']
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label = f"Side Referee {conf:.2f}"
        color = class_colors['Side Referee']
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated_frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # En güvenilir Main Referee kutusunu çiz
    if top_main_referee:
        box = top_main_referee['box']
        conf = top_main_referee['conf']
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label = f"Main Referee {conf:.2f}"
        color = class_colors['Main Referee']
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated_frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # En güvenilir top kutusunu çiz
    if top_ball:
        box = top_ball['box']
        conf = top_ball['conf']
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label = f"Ball {conf:.2f}"
        color = class_colors['Ball']
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated_frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Göster (dilersen çözünürlüğü ayarla)
    result = cv2.resize(annotated_frame, (1080, 720))
    cv2.imshow("YOLOv8 Detection", result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
