import os
import random
import shutil

# Lấy file image, label
def get_files(img_dir, lbl_dir):
    data = []
    for f in os.listdir(img_dir):
        if f.endswith(".jpg"):
            img = os.path.join(img_dir, f)
            lbl = os.path.join(lbl_dir, f.rsplit(".",1)[0]+".txt")
            if os.path.exists(lbl):
                data.append((img, lbl))
    return data

# Dữ liệu có tỉ lệ train, val 80:20
def split(data):
    random.shuffle(data)
    n = len(data)
    return data[:int(0.8*n)], data[int(0.8*n):]

if __name__ == '__main__':
    day = get_files("data/daytime-dataset/daytime/images",
                    "data/daytime-dataset/daytime/labels")

    night = get_files("data/nighttime-dataset/nighttime/images",
                      "data/nighttime-dataset/nighttime/labels")

    # Tạo train, val và cân bằng dữ liệu
    night = random.sample(night, len(day))
    day_train, day_val = split(day)
    night_train, night_val = split(night)
    train = day_train + night_train
    val   = day_val   + night_val
    random.shuffle(train)
    random.shuffle(val)

    # Copy sang folder chuẩn
    for s in ["train", "val"]:
        os.makedirs(f"vehicles_dataset/images/{s}", exist_ok=True)
        os.makedirs(f"vehicles_dataset/labels/{s}", exist_ok=True)
    for split_name, data in [("train", train), ("val", val)]:
        for img, lbl in data:
            shutil.copy(img, f"vehicles_dataset/images/{split_name}")
            shutil.copy(lbl, f"vehicles_dataset/labels/{split_name}")
            
    # Chuẩn hoá dữ liệu về cùng label
    for root, _, files in os.walk("vehicles_dataset/labels"):
        for f in files:
            if f.endswith(".txt"):
                path = os.path.join(root, f)
                new_lines = []
                with open(path) as file:
                    for line in file:
                        parts = line.split()
                        if not parts:
                            continue
                        cls = int(parts[0])
                        if cls >= 4:
                            cls -= 4
                        parts[0] = str(cls)
                        new_lines.append(" ".join(parts))
                with open(path, "w") as file:
                    file.write("\n".join(new_lines))

    print("Done!")