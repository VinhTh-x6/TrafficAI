import cv2
from ultralytics import YOLO

if __name__ == "__main__":
    model = YOLO(r"D:\TrafficAI\runs\detect\train\weights\best.pt")
    cap = cv2.VideoCapture(r"D:\TrafficAI\test.mp4")
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

    # w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # fps = int(cap.get(cv2.CAP_PROP_FPS))

    # out = cv2.VideoWriter(
    #     "output.mp4",
    #     cv2.VideoWriter_fourcc(*"mp4v"),
    #     fps,
    #     (w, h)
    # )

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # vẽ line giữa frame để đếm xe đi qua
        line = frame.shape[0] // 2
        cv2.line(frame, (0, line), (frame.shape[1], line), (255, 255, 255), 2)
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
                        if y_prev >= line and y_curr < line:
                            class_counts[model.names[int(cl)]] += 1
                            id_set.add(id)
                # lable và màu sắc theo class
                lable = model.names[int(cl)]
                color = colors.get(lable, (255,64,64))
                # vẽ bbox, tâm bbox, text
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.circle(frame, (cx, cy), 2, (191,62,255), -1)
                cv2.putText(frame, f"{lable} ID:{id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
        for i, (k, v) in enumerate(class_counts.items()):
            cv2.putText(frame, f"{k}: {v}", (20, 20 + i*30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors.get(k, (255,64,64)), 2)
        cv2.imshow("Frame", frame)
        # out.write(frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()