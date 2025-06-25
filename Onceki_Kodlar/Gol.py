import cv2
from ultralytics import YOLO
import numpy as np
from sklearn.cluster import KMeans
from datetime import datetime
# Modeli yükle
model = YOLO("../model/bestdeneme.pt")

# Video dosyasını aç
video_path = "../Videos/Kayseri_Samsunspor.mp4"
cap = cv2.VideoCapture(video_path)

class_names = ['Player', 'GoalKeeper', 'Ball', 'Main Referee', 'Side Referee', 'Staff Member']
class_thresholds = {'Side Referee': 0.5, 'Main Referee': 0.5, 'Player': 0.63, 'Staff Member': 0.7, 'Ball': 0.5, 'GoalKeeper': 0.5}
class_colors = {
    'Samsunspor': (0, 255, 0),
    'Kayserispor': (0, 140, 255),
    'Ball': (0, 0, 255),
    'Side Referee': (255, 0, 0),
    'Main Referee': (255, 100, 0),
    'Staff Member': (128, 0, 128),
    'GoalKeeper': (0, 255, 255)
}

Kayserispor = cv2.imread("../Forma/Kayserispor.png")
Hsv_Kayserispor = cv2.cvtColor(Kayserispor, cv2.COLOR_BGR2HSV)
ortalama_kayserispor = np.array(cv2.mean(Hsv_Kayserispor)[:3])

Samsunspor = cv2.imread("../Forma/Samsunspor.png")
Hsv_Samsunspor = cv2.cvtColor(Samsunspor, cv2.COLOR_BGR2HSV)
ortalama_samsunspor = np.array(cv2.mean(Hsv_Samsunspor)[:3])

team_a_color = ortalama_kayserispor if ortalama_kayserispor[1] < ortalama_samsunspor[1] else ortalama_samsunspor
team_b_color = ortalama_samsunspor if team_a_color is ortalama_kayserispor else ortalama_kayserispor

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

    kmeans = KMeans(n_clusters=2, random_state=0).fit(hsv_values)
    global team_a_color, team_b_color
    colors = kmeans.cluster_centers_
    if colors[0][1] < colors[1][1]:
        team_a_color, team_b_color = colors[0], colors[1]
    else:
        team_a_color, team_b_color = colors[1], colors[0]
    return True

def classify_player(hsv_value):
    dist_to_a = np.linalg.norm(hsv_value - team_a_color)
    dist_to_b = np.linalg.norm(hsv_value - team_b_color)
    return "Samsunspor" if dist_to_a < dist_to_b else "Kayserispor"

def detect_closest_team_to_ball(ball_box, player_boxes, frame):
    bx1, by1, bx2, by2 = map(int, ball_box.xyxy[0])
    ball_center = np.array([(bx1 + bx2) // 2, (by1 + by2) // 2])
    min_dist = float('inf')
    closest_team = "Unknown"
    for box in player_boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        player_center = np.array([(x1 + x2) // 2, (y1 + y2) // 2])
        dist = np.linalg.norm(ball_center - player_center)
        if dist < min_dist:
            min_dist = dist
            hsv_mean = get_hsv_mean(frame, box)
            closest_team = classify_player(hsv_mean)
    return closest_team

def estimate_goal_area(goalkeeper_box, frame_shape):
    x1, y1, x2, y2 = map(int, goalkeeper_box.xyxy[0])
    w = frame_shape[1]
    h = frame_shape[0]
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    goal_width = int(w * 0.18)
    goal_height = int(h * 0.25)
    gx1 = max(0, center_x - goal_width // 2)
    gx2 = min(w, center_x + goal_width // 2)
    gy1 = max(0, center_y - goal_height // 2)
    gy2 = min(h, center_y + goal_height // 2)
    return (gx1, gy1, gx2, gy2)

def is_goal(ball_box, goal_area):
    x1, y1, x2, y2 = map(int, ball_box.xyxy[0])
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    gx1, gy1, gx2, gy2 = goal_area
    return gx1 <= cx <= gx2 and gy1 <= cy <= gy2

initialized = False
goal_counts = {'Kayserispor': 0, 'Samsunspor': 0}

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    result = results[0]
    boxes = result.boxes
    annotated_frame = frame.copy()
    player_boxes = [box for box in boxes if class_names[int(box.cls[0].item())] == 'Player']
    if not initialized and len(player_boxes) >= 9:
        if initialize_team_colors(player_boxes, frame):
            initialized = True
            print("Takım renkleri başarıyla belirlendi!")

    top_ball = None
    goalkeeper_box = None

    for box in boxes:
        cls_id = int(box.cls[0].item())
        conf = box.conf[0].item()
        class_name = class_names[cls_id]
        if conf < class_thresholds.get(class_name, 0.5):
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        if class_name == 'GoalKeeper':
            goalkeeper_box = box
            label = f"GoalKeeper {conf:.2f}"
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), class_colors['GoalKeeper'], 2)
            cv2.putText(annotated_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, class_colors['GoalKeeper'], 2)

        elif class_name == 'Player':
            hsv_mean = get_hsv_mean(frame, box)
            team = classify_player(hsv_mean) if initialized else "Unknown"
            label = f"{team} {conf:.2f}"
            color = class_colors.get(team, (255, 255, 255))
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        elif class_name == 'Ball':
            if top_ball is None or conf > top_ball['conf']:
                top_ball = {'box': box, 'conf': conf}

    # GOL KONTROLÜ
    if top_ball and goalkeeper_box and initialized:
        goal_area = estimate_goal_area(goalkeeper_box, frame.shape)
        if is_goal(top_ball['box'], goal_area):
            shot_team = detect_closest_team_to_ball(top_ball['box'], player_boxes, frame)
            goal_counts[shot_team] += 1
            print(f"GOOOLLLL! {shot_team} gol attı!")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"..//Goller/{shot_team}_{timestamp}.jpg"
            cv2.imwrite(filename, annotated_frame)

    # Topu çiz
    if top_ball:
        box = top_ball['box']
        conf = top_ball['conf']
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label = f"Ball {conf:.2f}"
        color = class_colors['Ball']
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Gol Sayılarını Göster
    cv2.putText(annotated_frame, f"Kayserispor Goller: {goal_counts['Kayserispor']}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, class_colors['Kayserispor'], 2)
    cv2.putText(annotated_frame, f"Samsunspor Goller: {goal_counts['Samsunspor']}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, class_colors['Samsunspor'], 2)

    cv2.imshow("YOLOv8 Detection", cv2.resize(annotated_frame, (1080, 720)))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
