from ultralytics import YOLO

model = YOLO(r"models/best.pt")
model.predict(
    source=r"test_videos/test.mp4",
    imgsz=960,
    conf=0.25,
    device=0,
    line_width=1,
    show=True
)
