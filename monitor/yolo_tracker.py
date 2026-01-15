import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

ACTUAL_TOTAL = 50

def calculate_accuracy(detected, actual):
    if actual == 0:
        return 100.0
    acc = (1 - abs(detected - actual) / actual) * 100
    return max(0, min(100, acc))

# Load once
model = YOLO("yolov8n.pt")
tracker = DeepSort(max_age=30)

def process_video(source):
    cap = cv2.VideoCapture(source)
    unique_ids = set()
    frame_count = 0

    if not cap.isOpened():
        print("❌ Cannot open video:", source)
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 3 != 0:
            continue

        results = model(frame, conf=0.5, verbose=False)[0]
        detections = []

        for box in results.boxes:
            if int(box.cls[0]) == 0:  # person
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append(
                    ([x1, y1, x2-x1, y2-y1], float(box.conf[0]), "person")
                )

        tracks = tracker.update_tracks(detections, frame=frame)

        for track in tracks:
            if not track.is_confirmed():
                continue

            unique_ids.add(track.track_id)
            l, t, r, b = map(int, track.to_ltrb())
            cv2.rectangle(frame, (l, t), (r, b), (0,255,0), 2)
            cv2.putText(frame, f"ID {track.track_id}", (l, t-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

        count = len(unique_ids)
        accuracy = calculate_accuracy(count, ACTUAL_TOTAL)

        cv2.putText(frame, f"Total: {count}", (20,40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        cv2.putText(frame, f"Accuracy: {accuracy:.2f}%", (20,80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)

        _, buffer = cv2.imencode(".jpg", frame)
        yield buffer.tobytes(), count, accuracy

    cap.release()
