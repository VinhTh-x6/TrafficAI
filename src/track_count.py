import cv2
from ultralytics import YOLO
import numpy as np
import os
import subprocess
import tempfile
import uuid

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

    # process each frame, return the frame with drawn bounding boxes and updated vehicle counts
    def process_frame(self, frame):
        # use the model to detect and track vehicles
        results = self.model.track(
            source=frame,
            imgsz=640,
            conf=self.conf,
            tracker="bytetrack.yaml",
            persist=True
        )
        # draw line if present
        if self.mode == "line" and self.show_region and self.line_points is not None:
            p1, p2 = self.line_points
            cv2.line(frame, p1, p2, (255, 181, 197), 2)
            cv2.circle(frame, p1, 3, (255, 181, 197), -1)
            cv2.circle(frame, p2, 3, (255, 181, 197), -1)

        boxes = results[0].boxes
        if boxes is None or boxes.id is None:
            return frame
        # get bounding box info, ID and class of the object
        ids = boxes.id.cpu().numpy().astype(int)
        xyxy = boxes.xyxy.cpu().numpy()
        cls = boxes.cls.cpu().numpy().astype(int)

        for box, id, cl in zip(xyxy, ids, cls):
            x1, y1, x2, y2 = map(int, box)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            # get class name and corresponding color
            label = self.model.names[int(cl)]
            color = self.colors.get(label, (255,64,64))
            if self.mode == "polygon":
                self._count_polygon(id, cx, cy, label)
            elif self.mode == "line":
                self._count_line(id, cx, cy, label)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
            cv2.circle(frame, (cx, cy), 1, (191,62,255), -1)
            # class name and ID of the object
            text = f"#{id} {label}"
            (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)
            cv2.rectangle(frame, (x1, y1 - text_h - 2), (x1 + text_w + 2, y1), color, -1)
            cv2.putText(frame, text, (x1 + 1, y1 - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, cv2.LINE_AA)

        # draw polygon region if present
        if self.mode == "polygon" and self.region_points is not None and self.show_region:
            over = frame.copy()
            cv2.fillPoly(over, [self.region_points], (255, 181, 197))
            alpha = 0.3
            frame = cv2.addWeighted(over, alpha, frame, 1 - alpha, 0)
            cv2.polylines(frame, [self.region_points], True, (255, 181, 197), 1)
        return frame
    
    # count vehicles crossing the line
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

    # count vehicles inside the polygon
    def _count_polygon(self, id, cx, cy, label):
        if self.region_points is None:
            return
        inside = cv2.pointPolygonTest(self.region_points, (cx, cy), False) >= 0
        if inside and id not in self.counted_ids:
            if label in self.class_counts:
                self.class_counts[label] += 1
                self.counted_ids.add(id)


# ------------------------------------------------------------------
# Video encoding helpers
#   cv2.VideoWriter with fourcc 'H264' is almost NEVER available in the
#   opencv-python build installed via pip (encoder missing due to
#   licensing) — the writer silently fails to initialize and no frames
#   get written, but the old code never checked out.isOpened() so no
#   error was ever raised.
#   Solution: write using 'mp4v' (always available) to a temp file,
#   then re-encode to real H.264 using ffmpeg — a codec every browser
#   can play via the <video> tag.
# ------------------------------------------------------------------
def _get_ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def _reencode_to_h264(src_path, dst_path):
    """Re-encode src_path (mp4v) to H.264 (yuv420p, faststart) at dst_path."""
    ffmpeg_exe = _get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, "-y",
        "-i", src_path,
        "-vcodec", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "23",
        "-movflags", "+faststart",
        dst_path,
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg not found. Run: pip install imageio-ffmpeg "
            "(or install ffmpeg manually and add it to PATH)."
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg re-encode failed: {e.stderr.decode(errors='ignore')}")


# generator function to process the video and yield frames with drawn bounding boxes along with the vehicle counts
def tracking_counting(source, model_path, output_path="output.mp4", mode="polygon", 
                      region_points=None, location=None, conf=0.25, show_region=True):
    # open video 
    cap = cv2.VideoCapture(source)
    assert cap.isOpened(), "Cannot open source"

    counter = VehicleCounter(model_path, mode=mode, conf=conf, show_region=show_region)
    # get video parameters to create the output video and process frames
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or fps is None:
        fps = 25
    # define polygon/line 
    line_points = None
    if location == "Cầu Giấy - Trần Quý Kiên - C167.10-PTZ":
        region_points = np.array([[168, 82], [403, 93], [426, 159], [86, 143]], dtype=np.int32).reshape((-1, 1, 2))
        line_points = ((129, 111), (411, 125))
    elif location == "Cầu Giấy - Trần Đăng Ninh - C166.10-PTZ":
        region_points = np.array([[209, 95], [432, 133], [420, 191], [105, 129]], dtype=np.int32).reshape((-1, 1, 2))
        line_points = ((144, 113), (431, 161))
    counter.region_points = region_points
    counter.line_points = line_points

    # write to a TEMP file using mp4v (always available) — will be re-encoded to H.264 in the next step
    tmp_raw_path = os.path.join(tempfile.gettempdir(), f"raw_{uuid.uuid4().hex}.mp4")
    out = cv2.VideoWriter(tmp_raw_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (452, 256))
    if not out.isOpened():
        cap.release()
        raise RuntimeError(
            f"Failed to initialize VideoWriter for temp file '{tmp_raw_path}'. "
            "Check whether the mp4v codec is available in the installed OpenCV build."
        )

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # resize frame to match region_points
        frame = cv2.resize(frame, (452, 256))
        frame = counter.process_frame(frame)
        out.write(frame)
        # yield the frame with drawn bounding boxes and the vehicle counts to update the UI
        yield frame, counter.class_counts
    # release resources
    cap.release()
    out.release()

    # re-encode the temp file to real H.264 before returning output_path
    _reencode_to_h264(tmp_raw_path, output_path)
    if os.path.exists(tmp_raw_path):
        os.remove(tmp_raw_path)

if __name__ == "__main__":
    print("Done!")