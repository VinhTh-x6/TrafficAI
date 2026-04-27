import cv2
from ultralytics import YOLO

def tracking_counting(video_path, model_path, output_path="output.mp4"):
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_path)
    # Lấy thông số video
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Tạo writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    track_list = dict()
    id_set = set()
    class_counts = {
        "motorbike": 0,
        "car": 0,          
        "bus": 0,         
        "truck": 0 
    }
    colors = {
        "motorbike": (0,191,255),
        "car": (124,252,0),          
        "bus": (255,0,0),         
        "truck": (255,64,64)      
    }

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # vẽ line giữa frame để đếm xe đi qua
        line = frame.shape[0] // 2
        # cv2.line(frame, (0, line), (frame.shape[1], line), (255, 255, 255), 2)
        # Tracking với Bytetrack
        results = model.track(
            source=frame,
            imgsz=960,
            conf=0.25,
            tracker="bytetrack.yaml",
            line_width=1,
            persist=True
        )
        # lấy thông tin bounding box, ID và class của từng đối tượng được theo dõi
        boxes = results[0].boxes
        if boxes is not None and boxes.id is not None:
            ids = boxes.id.cpu().numpy().astype(int)
            xyxy = boxes.xyxy.cpu().numpy() 
            clf = boxes.cls.cpu().numpy().astype(int)

            for box, id, cl in zip(xyxy, ids, clf):
                x1, y1, x2, y2 = map(int, box)
                # center point của bounding box
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                # theo dõi vị trí của từng ID qua các frame và đếm khi chúng đi qua line
                if id not in track_list:
                    track_list[id] = []
                track_list[id].append((cx, cy))
                if len(track_list[id]) > 2:
                    track_list[id].pop(0)
                if len(track_list[id]) == 2:
                    y_prev = track_list[id][0][1]
                    y_curr = track_list[id][1][1]
                    if id not in id_set:
                        # đếm xe khi chúng đi qua line từ duới lên trên
                        if y_prev >= line and y_curr < line:
                            class_counts[model.names[int(cl)]] += 1
                            id_set.add(id)
                
                label = model.names[int(cl)]
                color = colors.get(label, (255,64,64))
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.circle(frame, (cx, cy), 2, (191,62,255), -1)
                # Tên class và ID của đối tượng
                text = f"{label} ID:{id}"
                (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                pad = 4
                cv2.rectangle(frame, (x1, y1 - text_h - 2 * pad), (x1 + text_w + 2 * pad, y1), color, -1)
                cv2.putText(frame, text, (x1 + pad, y1 - pad), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        out.write(frame)
        yield frame, class_counts    
    cap.release()

if __name__ == "__main__":
    print("Hello world")