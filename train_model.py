from ultralytics import YOLO

def train_model(resume=False):
    if resume:
        model = YOLO(r"D:\TrafficAI\runs\detect\train\weights\last.pt")
        model.train(resume=True)
    else:
        model = YOLO("yolov8s.pt")
        model.train(
            data="vehicles.yaml",
            epochs=100,
            imgsz=960,
            batch=8,
            device=0,
            rect=True,
            workers=4,
            cache=True
        )

if __name__ == "__main__":
    train_model(True)