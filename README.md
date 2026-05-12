# 🚦 TrafficAI: Hệ thống phát hiện, theo dõi và đếm phương tiện lưu thông trong giao thông ở Việt Nam

![Python](https://img.shields.io/badge/Python-3.x-blue)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

![demo](demo/demo1.gif)

---

## ✨ Tính năng

- Phát hiện phương tiện giao thông theo thời gian thực
- Theo dõi đối tượng bằng ByteTrack
- Đếm số lượng phương tiện theo luồng giao thông
- Hiển thị kết quả trực quan bằng Streamlit dashboard
- Hỗ trợ nhiều loại phương tiện: ô tô, xe máy, xe buýt, xe tải

---

## 📂 Dataset

- Dataset phương tiện Việt Nam từ Kaggle  
📎
https://www.kaggle.com/datasets/duongtran1909/vietnamese-vehicles-dataset
- Video giao thông thực tế tại Việt Nam  
- Một số nguồn dữ liệu công khai trên Internet  

---

## ⚙️ Cài đặt

```bash
git clone <repository-link>
cd <project-folder>
pip install -r requirements.txt
```

---

## ▶️ Chạy ứng dụng

```bash
streamlit run ./src/app.py
```

---

## 🧠 Huấn luyện mô hình

- Framework: YOLOv8 (Ultralytics)
- GPU: NVIDIA RTX 4060 Laptop GPU
- Dataset: bộ dữ liệu phương tiện giao thông Việt Nam  

Kết quả sau khi huấn luyện:
![training-results](demo/results.png)

Test trên video thực:
![test1-results](demo/test1.png)
![test2-results](demo/test2.png)

---

## 📊 Kết quả trên Streamlit

![demo1](demo/demo1.png)

![demo2](demo/demo2.png)

![demo3](demo/demo3.png)

![demo4](demo/demo4.png)

![demo5](demo/demo5.png)

---

## 🛠️ Công nghệ sử dụng

### 🤖 AI / Computer Vision
- YOLOv8 (Ultralytics)
- ByteTrack
- OpenCV

### 📊 Data Processing
- Pandas
- NumPy

### 📈 Visualization
- Plotly
- Matplotlib
- Seaborn

### 🌐 Web App
- Streamlit