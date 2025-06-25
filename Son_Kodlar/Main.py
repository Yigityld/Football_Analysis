import multiprocessing
import cv2
import numpy as np
from ultralytics import YOLO
from sklearn.cluster import KMeans
from interface import AppManager  # Arayüz için

def extract_jersey_hsv(path):
    img = cv2.imread(path)
    if img is None:
        print(f"Forma dosyası okunamadı: {path}")
        return None
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return np.array(cv2.mean(hsv)[:3])

def get_hsv_mean(image, box):
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cropped = image[y1:y2, x1:x2]
    if cropped.size == 0:
        return np.array([0, 0, 0])
    hsv_image = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
    return np.array(cv2.mean(hsv_image)[:3])

def initialize_team_colors(player_boxes, frame):
    hsv_values = []
    for box in player_boxes:
        hsv_mean = get_hsv_mean(frame, box)
        if hsv_mean is not None and hsv_mean.any():
            hsv_values.append(hsv_mean)

    if len(hsv_values) < 2:
        return None, None

    kmeans = KMeans(n_clusters=2, random_state=0).fit(hsv_values)
    global team_a_color, team_b_color
    colors = kmeans.cluster_centers_
    # Saturation küçük olan takım A olsun
    if colors[0][1] < colors[1][1]:
        return colors[0], colors[1]
    else:
        return colors[1], colors[0]


def classify_player(hsv_value, team_a_color, team_b_color, team_a_name, team_b_name):
    if team_a_color is None or team_b_color is None:
        return "Unknown"
    dist_to_a = np.linalg.norm(hsv_value - team_a_color)
    dist_to_b = np.linalg.norm(hsv_value - team_b_color)

    return team_a_name if dist_to_a < dist_to_b else team_b_name

def main(pipe):
    while True:
        if pipe.poll():
            data = pipe.recv()
            if data.get("start_summary"):
                print("✅ Özet başlatılıyor...")
                break
    model = YOLO("..//model/bestdeneme.pt")
    cap = cv2.VideoCapture("..//Videos//Kayseri_Samsunspor.mp4")

    class_names = ['Player', 'GoalKeeper', 'Ball', 'Main Referee', 'Side Referee', 'Staff Member']
    class_thresholds = {
        'Side Referee': 0.5,
        'Main Referee': 0.5,
        'Player': 0.63,
        'Staff Member': 0.7,
        'Ball': 0.5,
        'GoalKeeper': 0.5
    }

    team_a_name, team_b_name = "Team A", "Team B"
    team_a_color, team_b_color = None, None
    main_ref_name, side_ref_name = "Main Referee", "Side Referee"

    class_colors = {
        'Ball': (0, 0, 255),
        'Main Referee': (255, 255, 0),
        'Side Referee': (255, 0, 0),
        'Staff Member': (128, 0, 128),
        'GoalKeeper': (0, 255, 255),
    }

    initialized = False
    kontrol = 0
    Isim_kontrol1 = False
    Isim_kontrol2 = False
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if pipe.poll():
            data = pipe.recv()
            if 'team_a' in data and data.get('team_a_jersey'):
                team_a_name_temp = data['team_a']
                color_a = extract_jersey_hsv(data['team_a_jersey'])
                print(team_a_name_temp,  color_a)


            if 'team_b' in data and data.get('team_b_jersey'):
                team_b_name_temp = data['team_b']
                color_b = extract_jersey_hsv(data['team_b_jersey'])
                print(color_b)


            # Her iki forma da geldiyse, saturasyona göre Team A/B olarak ata
            if 'color_a' in locals() and 'color_b' in locals() and color_a is not None and color_b is not None and kontrol ==0:
                if color_a[1] < color_b[1]:
                    team_a_color = color_a
                    team_b_color = color_b
                    team_a_name = team_a_name_temp
                    team_b_name = team_b_name_temp
                    Isim_kontrol1 = True

                else:
                    team_a_color = color_a
                    team_b_color = color_b
                    team_a_name = team_b_name_temp
                    team_b_name = team_a_name_temp
                    Isim_kontrol2 = True
                kontrol +=1

            if Isim_kontrol1:
                team_a_name = team_a_name_temp
                team_b_name = team_b_name_temp

            if Isim_kontrol2:
                team_a_name = team_b_name_temp
                team_b_name = team_a_name_temp
            class_colors[team_a_name] = (0, 255, 0)
            class_colors[team_b_name] = (0, 140, 255)
            if 'main_ref' in data:
                main_ref_name = data['main_ref'] if data['main_ref'] else "Main Referee"
            if 'side_ref' in data:
                side_ref_name = data['side_ref'] if data['side_ref'] else "Side Referee"

        result = model.predict(source=frame, verbose=False)[0]
        annotated = frame.copy()

        boxes = result.boxes
        player_boxes = [box for box in boxes if class_names[int(box.cls[0].item())] == 'Player']

        # Eğer forma dosyası renkleri yoksa ve oyuncu kutuları yeterliyse otomatik renklere başlat
        if not initialized and len(player_boxes) >= 14 and team_a_color is not None:
            team_a_color, team_b_color = initialize_team_colors(player_boxes, frame)
            initialized = True
            print("Takım renkleri otomatik belirlendi")


        top_main, top_side, top_ball = None, None, None

        for box in boxes:
            cls_id = int(box.cls[0].item())
            conf = box.conf[0].item()
            class_name = class_names[cls_id]

            if conf < class_thresholds.get(class_name, 0.5):
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if class_name == 'Player':
                hsv = get_hsv_mean(frame, box)
                team = classify_player(hsv, team_a_color, team_b_color, team_a_name, team_b_name)
                label = f"{team} "
                color = class_colors.get(team, (255, 255, 255))
            elif class_name == 'Main Referee':
                if not top_main or conf > top_main['conf']:
                    top_main = {'box': box, 'conf': conf}
                continue
            elif class_name == 'Side Referee':
                if not top_side or conf > top_side['conf']:
                    top_side = {'box': box, 'conf': conf}
                continue
            elif class_name == 'Ball':
                if not top_ball or conf > top_ball['conf']:
                    top_ball = {'box': box, 'conf': conf}
                continue
            else:
                label = f"{class_name} "
                color = class_colors.get(class_name, (255, 255, 255))

            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Hakemleri isimle göster
        for ref, name, key in [(top_main, main_ref_name, 'Main Referee'), (top_side, side_ref_name, 'Side Referee')]:
            if ref:
                box = ref['box']
                conf = ref['conf']
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                color = class_colors[key]
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                cv2.putText(annotated, f"{name} ", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        if top_ball:
            box = top_ball['box']
            conf = top_ball['conf']
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            color = class_colors['Ball']
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated, f"Ball", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        resized = cv2.resize(annotated, (760, 640))
        cv2.imshow("Match Viewer", resized)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    pipe_parent, pipe_child = multiprocessing.Pipe()
    p = multiprocessing.Process(target=AppManager, args=(pipe_child,))
    p.start()

    main(pipe_parent)
    p.terminate()