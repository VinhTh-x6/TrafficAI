import os
import shutil

if __name__ == '__main__':
    root = "data/nighttime-dataset/nighttime"
    # root = "data/daytime-dataset/daytime"
    img_dir = os.path.join(root, "images")
    txt_dir = os.path.join(root, "labels")

    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(txt_dir, exist_ok=True)

    for file in os.listdir(root):
        path = os.path.join(root, file)
        if not os.path.isfile(path):
            continue
        ext = file.lower()
        if ext.endswith(".jpg"):
            shutil.move(path, os.path.join(img_dir, file))
        elif ext.endswith(".txt"):
            shutil.move(path, os.path.join(txt_dir, file))
            
    print("Done!")