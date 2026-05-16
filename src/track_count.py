import cv2
from ultralytics import YOLO
import numpy as np

class VehicleCounter:
    def __init__(self, model_path, mode="polygon", region_points=None, conf=0.25, show_region=True):
        self.model = YOLO(model_path)
        self.mode = mode
        self.region_points = region_points
        self.line_points = None
        self.conf = conf
        self.show_region = show_region
        self.class_counts = {
            "motorbike": 0,
            "car": 0,
            "bus": 0,
            "truck": 0
        }
        self.colors = {
            "motorbike": (255,191,0),
            "car": (0,205,102),
            "bus": (14,173,238),
            "truck": (64,64,255)
        }
        self.track_list = {}
        self.counted_ids = set()

    # xử lý từng frame, trả về frame đã vẽ bounding box và cập nhật đếm xe
    def process_frame(self, frame):
        # dùng model để detect và track xe
        results = self.model.track(
            source=frame,
            imgsz=640,
            conf=self.conf,
            tracker="bytetrack.yaml",
            persist=True
        )
        # vẽ line nếu có
        if self.mode == "line" and self.show_region and self.line_points is not None:
            p1, p2 = self.line_points
            cv2.line(frame, p1, p2, (255, 181, 197), 2)
            cv2.circle(frame, p1, 3, (255, 181, 197), -1)
            cv2.circle(frame, p2, 3, (255, 181, 197), -1)

        boxes = results[0].boxes
        if boxes is None or boxes.id is None:
            return frame
        # lấy thông tin bounding box, ID và class của đối tượng
        ids = boxes.id.cpu().numpy().astype(int)
        xyxy = boxes.xyxy.cpu().numpy()
        cls = boxes.cls.cpu().numpy().astype(int)

        for box, id, cl in zip(xyxy, ids, cls):
            x1, y1, x2, y2 = map(int, box)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            # lấy tên class và màu tương ứng
            label = self.model.names[int(cl)]
            color = self.colors.get(label, (255,64,64))
            if self.mode == "polygon":
                self._count_polygon(id, cx, cy, label)
            elif self.mode == "line":
                self._count_line(id, cx, cy, label)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
            cv2.circle(frame, (cx, cy), 1, (191,62,255), -1)
            # tên class và ID của đối tượng
            text = f"#{id} {label}"
            (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)
            cv2.rectangle(frame, (x1, y1 - text_h - 2), (x1 + text_w + 2, y1), color, -1)
            cv2.putText(frame, text, (x1 + 1, y1 - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, cv2.LINE_AA)

        # vẽ vùng polygon nếu có
        if self.mode == "polygon" and self.region_points is not None and self.show_region:
            over = frame.copy()
            cv2.fillPoly(over, [self.region_points], (255, 181, 197))
            alpha = 0.3
            frame = cv2.addWeighted(over, alpha, frame, 1 - alpha, 0)
            cv2.polylines(frame, [self.region_points], True, (255, 181, 197), 1)
        return frame
    
    # đếm xe qua line
    def _count_line(self, id, cx, cy, label):
        p1, p2 = self.line_points
        if id not in self.track_list:
            self.track_list[id] = []
        self.track_list[id].append((cx, cy))
        if len(self.track_list[id]) > 2:
            self.track_list[id].pop(0)
        if len(self.track_list[id]) == 2:
            prev_p = self.track_list[id][0]
            curr_p = self.track_list[id][1]
            prev_side = np.sign(
                (p2[0] - p1[0]) * (prev_p[1] - p1[1]) -
                (p2[1] - p1[1]) * (prev_p[0] - p1[0])
            )
            curr_side = np.sign(
                (p2[0] - p1[0]) * (curr_p[1] - p1[1]) -
                (p2[1] - p1[1]) * (curr_p[0] - p1[0])
            )
            if prev_side != curr_side:
                if id not in self.counted_ids:
                    if label in self.class_counts:
                        self.class_counts[label] += 1
                        self.counted_ids.add(id)

    # đếm xe qua polygon    
    def _count_polygon(self, id, cx, cy, label):
        if self.region_points is None:
            return
        inside = cv2.pointPolygonTest(self.region_points, (cx, cy), False) >= 0
        if inside and id not in self.counted_ids:
            if label in self.class_counts:
                self.class_counts[label] += 1
                self.counted_ids.add(id)

# generator function để xử lý video và trả về frame đã vẽ bounding box cùng với số lượng xe đếm được
def tracking_counting(source, model_path, output_path="output.mp4", mode="polygon", 
                      region_points=None, location=None, conf=0.25, show_region=True):
    # mở video 
    cap = cv2.VideoCapture(source)
    assert cap.isOpened(), "Cannot open source"

    counter = VehicleCounter(model_path, mode=mode, conf=conf, show_region=show_region)
    # lấy thông số video để tạo video output và xử lý frame
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or fps is None:
        fps = 25
    # định nghĩa polygon/line 
    line_points = None
    if location == "Cầu Giấy - Trần Quý Kiên - C167.10-PTZ":
        region_points = np.array([[168, 82], [403, 93], [426, 159], [86, 143]], dtype=np.int32).reshape((-1, 1, 2))
        line_points = ((129, 111), (411, 125))
    elif location == "Cầu Giấy - Trần Đăng Ninh - C166.10-PTZ":
        region_points = np.array([[209, 95], [432, 133], [420, 191], [105, 129]], dtype=np.int32).reshape((-1, 1, 2))
        line_points = ((144, 113), (431, 161))
    counter.region_points = region_points
    counter.line_points = line_points
    # tạo video writer để lưu video output
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'H264'), fps, ((452, 256)))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # resize frame tương ứng cho region_points
        frame = cv2.resize(frame, (452, 256))
        frame = counter.process_frame(frame)
        out.write(frame)
        # trả về frame đã vẽ bounding box và số lượng xe đếm được để cập nhật UI
        yield frame, counter.class_counts
    # giải phóng tài nguyên
    cap.release()
    out.release()

if __name__ == "__main__":
    print("Done!")
    