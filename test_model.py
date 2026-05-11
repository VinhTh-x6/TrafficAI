from ultralytics import YOLO

model = YOLO(r"D:\TrafficAI\models\best.pt")
model.predict(
    source=r"D:\TrafficAI\test.mp4",
    imgsz=960,
    conf=0.25,
    device=0,
    save=True,
    line_width=1,
    show=True
)
